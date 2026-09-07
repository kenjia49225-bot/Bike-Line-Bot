from django.test import TestCase

from .models import FAQ


class FAQModelTests(TestCase):
    def test_create_faq(self):
        faq = FAQ.objects.create(
            question='営業時間を教えてください。',
            answer='営業時間は 10:00〜19:00 です。',
        )
        self.assertEqual(faq.question, '営業時間を教えてください。')
        self.assertEqual(faq.answer, '営業時間は 10:00〜19:00 です。')
        self.assertEqual(FAQ.objects.count(), 1)

    def test_question_and_answer_are_saved(self):
        question = '駐輪場はありますか?'
        answer = '無料の駐輪場がございます。'
        faq = FAQ.objects.create(question=question, answer=answer)
        self.assertEqual(faq.question, question)
        self.assertEqual(faq.answer, answer)

    def test_is_active_defaults_to_true(self):
        faq = FAQ.objects.create(
            question='定休日はいつですか?',
            answer='毎週水曜日です。',
        )
        self.assertTrue(faq.is_active)

    def test_str_returns_question(self):
        faq = FAQ.objects.create(
            question='支払い方法を教えてください。',
            answer='現金・クレジットカードに対応しています。',
        )
        self.assertEqual(str(faq), '支払い方法を教えてください。')
