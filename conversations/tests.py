from django.test import TestCase

from .models import Conversation


class ConversationModelTests(TestCase):
    def test_create_conversation(self):
        conv = Conversation.objects.create(
            user_id='line-user-123',
            role=Conversation.Role.USER,
            content='営業時間を教えてください。',
        )
        self.assertEqual(conv.user_id, 'line-user-123')
        self.assertEqual(conv.role, Conversation.Role.USER)
        self.assertEqual(conv.content, '営業時間を教えてください。')
        self.assertEqual(Conversation.objects.count(), 1)

    def test_bot_role(self):
        conv = Conversation.objects.create(
            user_id='line-user-123',
            role=Conversation.Role.BOT,
            content='営業時間は 10:00〜19:00 です。',
        )
        self.assertEqual(conv.role, Conversation.Role.BOT)

    def test_str_returns_summary(self):
        conv = Conversation.objects.create(
            user_id='line-user-123',
            role=Conversation.Role.USER,
            content='こんにちは',
        )
        self.assertEqual(str(conv), 'line-user-123 (user): こんにちは')
