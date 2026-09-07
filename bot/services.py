from django.conf import settings

from conversations.models import Conversation

from .ai import HANDOFF_MESSAGE, generate_reply


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
    reply_text = generate_reply(text, user_id=user_id)
    is_handoff = reply_text == HANDOFF_MESSAGE
    save_message(user_id, Conversation.Role.BOT, reply_text, needs_human=is_handoff)
    return reply_text


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
