import json
from unittest import mock

from django.test import TestCase

from conversations.models import Conversation

from .ai import (
    HANDOFF_MESSAGE,
    _build_history,
    _rank_faqs,
    build_context,
    generate_ai_reply,
    generate_reply,
)
from .services import handle_text_message, save_message
from .views import _is_rate_limited


class BotServiceTests(TestCase):
    def test_save_message_creates_user_conversation(self):
        save_message('user-1', Conversation.Role.USER, 'こんにちは')
        self.assertEqual(Conversation.objects.count(), 1)
        conv = Conversation.objects.get()
        self.assertEqual(conv.user_id, 'user-1')
        self.assertEqual(conv.role, Conversation.Role.USER)
        self.assertEqual(conv.content, 'こんにちは')
        self.assertFalse(conv.needs_human)
        self.assertEqual(conv.status, Conversation.Status.OPEN)

    def test_save_message_marks_handoff(self):
        save_message('user-1', Conversation.Role.BOT, '引き継ぎます', needs_human=True)
        conv = Conversation.objects.get()
        self.assertTrue(conv.needs_human)
        self.assertEqual(conv.status, Conversation.Status.HANDOFF)

    @mock.patch('bot.ai.generate_ai_reply', return_value='営業時間は 10:00〜19:00 です。')
    def test_handle_text_message_saves_both_roles(self, mock_ai):
        reply = handle_text_message('user-2', '定休日はいつですか?')
        self.assertEqual(Conversation.objects.count(), 2)
        self.assertTrue(
            Conversation.objects.filter(user_id='user-2', role=Conversation.Role.USER).exists()
        )
        bot_conv = Conversation.objects.filter(user_id='user-2', role=Conversation.Role.BOT).get()
        self.assertFalse(bot_conv.needs_human)
        self.assertEqual(reply, '営業時間は 10:00〜19:00 です。')

    @mock.patch('bot.ai.generate_ai_reply', return_value=None)
    def test_handle_text_message_marks_handoff_on_no_answer(self, mock_ai):
        reply = handle_text_message('user-3', '分からない質問')
        self.assertEqual(reply, HANDOFF_MESSAGE)
        bot_conv = Conversation.objects.filter(user_id='user-3', role=Conversation.Role.BOT).get()
        self.assertTrue(bot_conv.needs_human)
        self.assertEqual(bot_conv.status, Conversation.Status.HANDOFF)

    @mock.patch('bot.notifications.notify_staff_handoff')
    @mock.patch('bot.ai.generate_ai_reply', return_value=None)
    def test_handoff_notifies_once_per_pending(self, mock_ai, mock_notify):
        handle_text_message('user-4', '1回目の質問')
        self.assertEqual(mock_notify.call_count, 1)
        # 2回目は未解決の引き継ぎが既にあるため通知しない
        handle_text_message('user-4', '2回目の質問')
        self.assertEqual(mock_notify.call_count, 1)


class AIReplyTests(TestCase):
    @mock.patch('bot.ai.generate_ai_reply', return_value='回答です。')
    def test_generate_reply_uses_ai_answer(self, mock_ai):
        self.assertEqual(generate_reply('質問'), '回答です。')

    @mock.patch('bot.ai.generate_ai_reply', return_value=None)
    def test_generate_reply_handoff_when_no_answer(self, mock_ai):
        self.assertEqual(generate_reply('質問'), HANDOFF_MESSAGE)

    @mock.patch('bot.ai.generate_ai_reply', side_effect=Exception('boom'))
    def test_generate_reply_handoff_on_error(self, mock_ai):
        self.assertEqual(generate_reply('質問'), HANDOFF_MESSAGE)

    def test_build_context_returns_string(self):
        self.assertIsInstance(build_context(), str)

    def test_build_context_filters_faqs_by_message(self):
        from faqs.models import FAQ

        FAQ.objects.create(question='営業時間は？', answer='10時から19時です。', is_active=True)
        FAQ.objects.create(question='支払い方法は？', answer='現金とカードです。', is_active=True)
        context = build_context('営業時間を教えてください')
        self.assertIn('営業時間は？', context)

    def test_rank_faqs_prioritizes_matching_faq(self):
        from faqs.models import FAQ

        FAQ.objects.create(question='営業時間は？', answer='10時から19時です。', is_active=True)
        FAQ.objects.create(question='支払い方法は？', answer='現金とカードです。', is_active=True)
        faqs = FAQ.objects.filter(is_active=True)
        ranked = _rank_faqs(faqs, '営業時間を教えてください', limit=3)
        self.assertEqual(ranked[0].question, '営業時間は？')

    def test_rank_faqs_respects_limit(self):
        from faqs.models import FAQ

        for q in ['質問1です', '質問2です', '質問3です']:
            FAQ.objects.create(question=q, answer='答', is_active=True)
        faqs = FAQ.objects.filter(is_active=True)
        ranked = _rank_faqs(faqs, '共通の単語', limit=2)
        self.assertLessEqual(len(ranked), 2)

    def test_build_history_reversed_and_limited(self):
        from .ai import HISTORY_LIMIT

        for i in range(HISTORY_LIMIT + 2):
            Conversation.objects.create(
                user_id='hist-user',
                role=Conversation.Role.USER,
                content=f'メッセージ{i}',
            )
        history = _build_history('hist-user')
        self.assertEqual(len(history), HISTORY_LIMIT)
        # 古い順（最初の要素が最も古い）
        self.assertLessEqual(history[0].created_at, history[-1].created_at)

    def test_build_history_empty_without_user(self):
        self.assertEqual(_build_history(None), [])

    @mock.patch('openai.OpenAI')
    def test_generate_ai_reply_returns_answer(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content='営業時間は10時からです。'))]
        mock_client.chat.completions.create.return_value = mock_response

        with self.settings(OPENAI_API_KEY='test-key'):
            reply = generate_ai_reply('営業時間は？')
        self.assertEqual(reply, '営業時間は10時からです。')

    @mock.patch('openai.OpenAI')
    def test_generate_ai_reply_handoff_when_ai_says_handoff(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content='HANDOFF'))]
        mock_client.chat.completions.create.return_value = mock_response

        with self.settings(OPENAI_API_KEY='test-key'):
            reply = generate_ai_reply('在庫はありますか？')
        self.assertIsNone(reply)

    def test_generate_ai_reply_no_api_key(self):
        with self.settings(OPENAI_API_KEY=''):
            self.assertIsNone(generate_ai_reply('こんにちは'))

    @mock.patch('openai.OpenAI')
    def test_generate_ai_reply_no_content(self, mock_openai_cls):
        mock_client = mock_openai_cls.return_value
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response

        with self.settings(OPENAI_API_KEY='test-key'):
            self.assertIsNone(generate_ai_reply('こんにちは'))


class WebhookViewTests(TestCase):
    def _make_text_event_body(self, user_id='line-user-1', text='こんにちは', reply_token='reply-1'):
        return {
            'destination': 'dummy',
            'events': [
                {
                    'type': 'message',
                    'replyToken': reply_token,
                    'source': {'type': 'user', 'userId': user_id},
                    'message': {'type': 'text', 'text': text},
                }
            ],
        }

    def test_webhook_requires_post(self):
        response = self.client.get('/bot/webhook/')
        self.assertEqual(response.status_code, 405)

    @mock.patch('bot.views.WebhookParser')
    @mock.patch('bot.views._reply')
    @mock.patch('bot.ai.generate_ai_reply', return_value='回答です。')
    def test_webhook_saves_conversation_and_replies(self, mock_ai, mock_reply, mock_parser):
        body = self._make_text_event_body(text='営業時間を教えて')
        from linebot.v3.webhooks import MessageEvent, TextMessageContent, UserSource

        event = MessageEvent(
            reply_token='reply-1',
            source=UserSource(user_id='line-user-1'),
            message=TextMessageContent(id='msg-1', quote_token='quote-1', text='営業時間を教えて'),
            timestamp=1700000000000,
            mode='active',
            webhook_event_id='evt-1',
            delivery_context={'is_redelivery': False},
        )
        mock_parser.return_value.parse.return_value = [event]

        with self.settings(LINE_CHANNEL_ACCESS_TOKEN='token', LINE_CHANNEL_SECRET='secret'):
            response = self.client.post(
                '/bot/webhook/',
                data=json.dumps(body),
                content_type='application/json',
                HTTP_X_LINE_SIGNATURE='sig',
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Conversation.objects.count(), 2)
        mock_reply.assert_called_once_with('token', 'reply-1', '回答です。')

    @mock.patch('bot.views.WebhookParser')
    @mock.patch('bot.views._reply')
    def test_webhook_image_message_marks_handoff(self, mock_reply, mock_parser):
        from linebot.v3.webhooks import ContentProvider, ImageMessageContent, MessageEvent, UserSource

        event = MessageEvent(
            reply_token='reply-1',
            source=UserSource(user_id='line-user-1'),
            message=ImageMessageContent(
                id='img-1', quote_token='quote-1',
                content_provider=ContentProvider(type='line'),
            ),
            timestamp=1700000000000,
            mode='active',
            webhook_event_id='evt-1',
            delivery_context={'is_redelivery': False},
        )
        mock_parser.return_value.parse.return_value = [event]

        with self.settings(LINE_CHANNEL_ACCESS_TOKEN='token', LINE_CHANNEL_SECRET='secret'):
            response = self.client.post(
                '/bot/webhook/',
                data=json.dumps({'events': []}),
                content_type='application/json',
                HTTP_X_LINE_SIGNATURE='sig',
            )

        self.assertEqual(response.status_code, 200)
        bot_conv = Conversation.objects.filter(role=Conversation.Role.BOT).get()
        self.assertTrue(bot_conv.needs_human)

    @mock.patch('bot.views.WebhookParser')
    def test_webhook_invalid_signature_returns_403(self, mock_parser):
        from linebot.v3.exceptions import InvalidSignatureError

        mock_parser.return_value.parse.side_effect = InvalidSignatureError('bad')

        response = self.client.post(
            '/bot/webhook/',
            data=json.dumps({'events': []}),
            content_type='application/json',
            HTTP_X_LINE_SIGNATURE='bad-sig',
        )
        self.assertEqual(response.status_code, 403)


class HealthViewTests(TestCase):
    def test_health_returns_200(self):
        response = self.client.get('/bot/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')


class RateLimitTests(TestCase):
    def test_allows_within_limit(self):
        from .models import RateLimit

        for _ in range(9):
            self.assertFalse(_is_rate_limited('user-1'))
        self.assertEqual(RateLimit.objects.get(user_id='user-1').count, 9)

    def test_blocks_over_limit(self):
        for _ in range(10):
            _is_rate_limited('user-2')
        self.assertTrue(_is_rate_limited('user-2'))
