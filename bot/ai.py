import logging

from django.conf import settings

from conversations.models import Conversation
from faqs.models import FAQ
from stores.models import Store

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 6


def build_context(user_message=None):
    """FAQ と店舗情報を AI への回答材料として集める。"""
    stores = Store.objects.all()
    faqs = FAQ.objects.filter(is_active=True)
    if user_message:
        faqs = _rank_faqs(faqs, user_message, limit=3)

    lines = []
    lines.append('以下は店舗の情報です。')
    for store in stores:
        lines.append(f'店舗名: {store.name}')
        lines.append(f'現在の営業状態: {"営業中" if store.is_open_now() else "営業時間外"}')
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


def _rank_faqs(faqs, user_message, limit=3):
    """文字オーバーラップによる簡易的な関連FAQ抽出（外部API不要）。"""
    message_chars = set(user_message)
    ranked = []
    for faq in faqs:
        question_chars = set(faq.question)
        overlap = len(message_chars & question_chars)
        if overlap:
            ranked.append((overlap, faq))
    ranked.sort(key=lambda x: x[0], reverse=True)
    if not ranked:
        return list(faqs)[:limit]
    return [faq for _, faq in ranked[:limit]]


def generate_ai_reply(user_message, user_id=None):
    """AI を呼んで回答を生成する。回答できない場合は None を返す。"""
    from openai import OpenAI

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return None

    context = build_context(user_message)
    system_prompt = (
        'あなたは自転車販売・修理店の LINE 問い合わせ対応アシスタントです。'
        '以下の店舗情報と FAQ を参考に、ユーザーの質問に日本語で簡潔に答えてください。'
        '参考情報で回答できない場合は、回答せず「HANDOFF」とだけ出力してください。'
        '\n\n'
        f'{context}'
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    for history in _build_history(user_id):
        role = 'assistant' if history.role == Conversation.Role.BOT else 'user'
        messages.append({'role': role, 'content': history.content})
    messages.append({'role': 'user', 'content': user_message})

    client = OpenAI(api_key=api_key, timeout=30.0)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
    )
    answer = response.choices[0].message.content
    if answer is None:
        return None
    answer = answer.strip()
    if answer == 'HANDOFF':
        return None
    return answer


def _build_history(user_id):
    """直近の会話履歴を古い順で返す（文脈として利用）。"""
    if not user_id:
        return []
    queryset = Conversation.objects.filter(user_id=user_id).order_by('-created_at')[:HISTORY_LIMIT]
    return list(reversed(queryset))


HANDOFF_MESSAGE = '申し訳ございません。お問い合わせの内容について、担当スタッフが後ほどご連絡いたします。少々お待ちください。'


def generate_reply(user_message, user_id=None):
    """AI で回答を試み、できない場合は人間への引き継ぎメッセージを返す。"""
    try:
        answer = generate_ai_reply(user_message, user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception('AI reply generation failed: %s', exc)
        answer = None

    if answer:
        return answer
    return HANDOFF_MESSAGE
