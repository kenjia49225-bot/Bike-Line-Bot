import logging

from django.conf import settings

from conversations.models import Conversation
from .services import push_message

logger = logging.getLogger(__name__)


def _staff_ids():
    raw = getattr(settings, 'STAFF_LINE_USER_IDS', '')
    if not raw:
        return []
    return [uid.strip() for uid in raw.split(',') if uid.strip()]


def notify_staff_handoff(user_id, question):
    """引き継ぎ発生時にスタッフへ通知する。二重通知は防ぐ。"""
    staff_ids = _staff_ids()
    if not staff_ids:
        logger.info('STAFF_LINE_USER_IDS が未設定のため通知をスキップします')
        return 0

    message = (
        '【要引き継ぎのお知らせ】\n'
        f'ユーザー: {user_id}\n'
        f'質問内容: {question}\n'
        '対応をお願いします。'
    )

    sent = 0
    for staff_id in staff_ids:
        try:
            push_message(staff_id, message)
            sent += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception('スタッフへの通知に失敗しました: %s', exc)
    return sent
