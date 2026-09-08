import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import ImageMessageContent, MessageEvent, TextMessageContent

from .services import handle_text_message

logger = logging.getLogger(__name__)

IMAGE_REPLY = '画像を確認いたしました。担当スタッフが内容を確認してご連絡いたします。'


def _is_rate_limited(user_id):
    """ユーザー単位のレート制限（DB ベース・複数ワーカーでも共有）。上限を超えたら True を返す。"""
    from datetime import timedelta

    from django.db import transaction
    from django.utils import timezone

    from .models import RateLimit

    now = timezone.now()
    window = timedelta(seconds=settings.RATE_LIMIT_WINDOW)

    with transaction.atomic():
        # 既存行はロックして原子的に更新、無ければ作成（初回は get_or_create で安全に処理）
        try:
            record = RateLimit.objects.select_for_update().get(user_id=user_id)
            created = False
        except RateLimit.DoesNotExist:
            record = RateLimit(user_id=user_id, count=0, window_start=now)
            created = True

        # ウィンドウが過ぎていたらリセット
        if not created and record.window_start < (now - window):
            record.count = 0
            record.window_start = now

        if record.count >= settings.RATE_LIMIT_MAX:
            return True

        record.count += 1
        record.save()

    return False


def _reply(access_token, reply_token, text):
    configuration = Configuration(access_token=access_token)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)],
            )
        )


@csrf_exempt
@require_POST
def webhook(request):
    channel_secret = settings.LINE_CHANNEL_SECRET
    access_token = settings.LINE_CHANNEL_ACCESS_TOKEN

    signature = request.headers.get('X-Line-Signature', '')
    body = request.body.decode('utf-8')

    parser = WebhookParser(channel_secret)
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        logger.warning('Invalid LINE webhook signature')
        return JsonResponse({'status': 'invalid signature'}, status=403)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        source = getattr(event.source, 'user_id', None)
        if not source:
            continue
        reply_token = event.reply_token
        if not reply_token:
            continue

        if _is_rate_limited(source):
            logger.warning('Rate limit exceeded for user %s', source)
            continue

        if isinstance(event.message, TextMessageContent):
            reply_text = handle_text_message(source, event.message.text)
        elif isinstance(event.message, ImageMessageContent):
            from .services import save_message
            from conversations.models import Conversation

            save_message(source, Conversation.Role.USER, '[画像]')
            save_message(source, Conversation.Role.BOT, IMAGE_REPLY, needs_human=True)
            reply_text = IMAGE_REPLY
        else:
            continue

        if access_token:
            try:
                _reply(access_token, reply_token, reply_text)
            except Exception as exc:  # noqa: BLE001
                logger.exception('Failed to reply to LINE: %s', exc)

    return JsonResponse({'status': 'ok'})
