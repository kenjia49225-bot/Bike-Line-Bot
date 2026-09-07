import logging

from django.conf import settings

from faqs.models import FAQ
from stores.models import Store

logger = logging.getLogger(__name__)


def build_context():
    """FAQ と店舗情報を AI への回答材料として集める。"""
    faqs = FAQ.objects.filter(is_active=True)
    stores = Store.objects.all()

    lines = []
    lines.append('以下は店舗の情報です。')
    for store in stores:
        lines.append(f'店舗名: {store.name}')
        if store.business_hours:
            lines.append(f'営業時間: {store.business_hours}')
        if store.closed_days:
            lines.append(f'定休日: {store.closed_days}')
        if store.access:
            lines.append(f'アクセス: {store.access}')
        if store.payment_methods:
            lines.append(f'支払い方法: {store.payment_methods}')
        if store.phone:
            lines.append(f'電話番号: {store.phone}')
        if store.address:
            lines.append(f'住所: {store.address}')
        lines.append('---')

    lines.append('以下はよくある質問と回答(FAQ)です。')
    for faq in faqs:
        lines.append(f'Q: {faq.question}')
        lines.append(f'A: {faq.answer}')
        lines.append('---')

    return '\n'.join(lines)


def generate_ai_reply(user_message):
    """AI を呼んで回答を生成する。回答できない場合は None を返す。"""
    from openai import OpenAI

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None

    context = build_context()
    system_prompt = (
        'あなたは自転車販売・修理店の LINE 問い合わせ対応アシスタントです。'
        '以下の店舗情報と FAQ を参考に、ユーザーの質問に日本語で簡潔に答えてください。'
        '参考情報で回答できない場合は、回答せず「HANDOFF」とだけ出力してください。'
        '\n\n'
        f'{context}'
    )

    client = OpenAI(api_key=api_key, timeout=30.0)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ],
    )
    answer = response.choices[0].message.content
    if answer is None:
        return None
    answer = answer.strip()
    if answer == 'HANDOFF':
        return None
    return answer


HANDOFF_MESSAGE = '申し訳ございません。お問い合わせの内容について、担当スタッフが後ほどご連絡いたします。少々お待ちください。'


def generate_reply(user_message):
    """AI で回答を試み、できない場合は人間への引き継ぎメッセージを返す。"""
    try:
        answer = generate_ai_reply(user_message)
    except Exception as exc:  # noqa: BLE001
        logger.exception('AI reply generation failed: %s', exc)
        answer = None

    if answer:
        return answer
    return HANDOFF_MESSAGE
