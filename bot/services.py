from conversations.models import Conversation

from .ai import generate_reply


def save_message(user_id, role, content):
    return Conversation.objects.create(
        user_id=user_id,
        role=role,
        content=content,
    )


def handle_text_message(user_id, text):
    save_message(user_id, Conversation.Role.USER, text)
    reply_text = generate_reply(text)
    save_message(user_id, Conversation.Role.BOT, reply_text)
    return reply_text
