from conversations.models import Conversation


def save_message(user_id, role, content):
    return Conversation.objects.create(
        user_id=user_id,
        role=role,
        content=content,
    )


def generate_reply(text):
    return f'ご質問ありがとうございます。ただいま準備中のため、担当者への引き継ぎを行います。\n（受信メッセージ: {text}）'


def handle_text_message(user_id, text):
    save_message(user_id, Conversation.Role.USER, text)
    reply_text = generate_reply(text)
    save_message(user_id, Conversation.Role.BOT, reply_text)
    return reply_text
