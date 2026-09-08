from django.core.cache import cache

from django.conf import settings

from conversations.models import Conversation

from .ai import HANDOFF_MESSAGE, generate_reply

INTAKE_KEYWORDS = ('予約', '修理', '修理受付', '直して', '故障', '見積もり')


def save_message(user_id, role, content, needs_human=False):
    return Conversation.objects.create(
        user_id=user_id,
        role=role,
        content=content,
        needs_human=needs_human,
        status=Conversation.Status.HANDOFF if needs_human else Conversation.Status.OPEN,
    )


def handle_text_message(user_id, text):
    save_message(user_id, Conversation.Role.USER, text)

    intake_reply = _handle_intake(user_id, text)
    if intake_reply is not None:
        save_message(user_id, Conversation.Role.BOT, intake_reply, needs_human=True)
        return intake_reply

    reply_text = generate_reply(text, user_id=user_id)
    is_handoff = reply_text == HANDOFF_MESSAGE
    save_message(user_id, Conversation.Role.BOT, reply_text, needs_human=is_handoff)
    if is_handoff and not _has_pending_handoff(user_id):
        from .notifications import notify_staff_handoff

        notify_staff_handoff(user_id, text)
    return reply_text


def _handle_intake(user_id, text):
    """予約・修理受付の開始判定およびフロー継続を処理する。"""
    from .intake import IntakeFlow

    flow = IntakeFlow(user_id)
    in_progress = cache.get(f'intake:{user_id}') is not None

    stripped = (text or '').strip()
    if in_progress:
        return flow.handle(text)

    if any(k in stripped for k in INTAKE_KEYWORDS):
        return flow.start(text)

    return None


def _has_pending_handoff(user_id):
    """同一ユーザーに未解決の引き継ぎが既に存在するか（二重通知防止）。"""
    return Conversation.objects.filter(
        user_id=user_id,
        needs_human=True,
        status=Conversation.Status.HANDOFF,
    ).exclude(content=HANDOFF_MESSAGE).exists()


def push_message(user_id, text):
    """LINE のプッシュ API で任意のユーザーにメッセージを送信する（人間からの返信など）。"""
    from linebot.v3.messaging import (
        ApiClient,
        Configuration,
        MessagingApi,
        PushMessageRequest,
        TextMessage,
    )

    access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
    if not access_token:
        return False

    configuration = Configuration(access_token=access_token)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=text)],
            )
        )
    return True
