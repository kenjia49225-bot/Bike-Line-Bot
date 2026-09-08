from django.core.cache import cache

from reservations.models import Reservation

CANCEL_KEYWORDS = ('キャンセル', 'やめる', '中止', 'cancel')


class IntakeFlow:
    """予約・修理受付の段階的入力フロー（状態はキャッシュで管理）。"""

    STEPS = ('kind', 'name', 'preferred_datetime', 'detail', 'phone')

    def __init__(self, user_id):
        self.user_id = user_id
        self.cache_key = f'intake:{user_id}'

    def _get_state(self):
        return cache.get(self.cache_key) or {'step': 'kind', 'data': {}}

    def _set_state(self, state):
        cache.set(self.cache_key, state, timeout=1800)

    def clear(self):
        cache.delete(self.cache_key)

    def start(self, text=''):
        kind = self._detect_kind(text)
        state = {'step': 'name', 'data': {'kind': kind}}
        self._set_state(state)
        return 'お名前を入力してください。'

    def handle(self, text):
        """入力を受け取り、次のプロンプトまたは完了メッセージを返す。"""
        if self._is_cancel(text):
            self.clear()
            return '受付をキャンセルしました。'

        state = self._get_state()
        step = state['step']
        data = state['data']

        if step == 'kind':
            return self.start(text)

        data[step] = text

        try:
            next_step = self.STEPS[self.STEPS.index(step) + 1]
        except IndexError:
            self.clear()
            return self._complete(data)

        state['step'] = next_step
        self._set_state(state)
        return self._prompt(next_step)

    def _detect_kind(self, text):
        if '修理' in text or '直して' in text or '故障' in text:
            return Reservation.Kind.REPAIR
        return Reservation.Kind.RESERVATION

    def _prompt(self, step):
        prompts = {
            'name': 'お名前を入力してください。',
            'preferred_datetime': '希望日時を入力してください（例: 明日の午後3時）。',
            'detail': '内容を入力してください。',
            'phone': '電話番号を入力してください（任意）。「なし」でも構いません。',
        }
        return prompts.get(step, '')

    def _complete(self, data):
        Reservation.objects.create(
            user_id=self.user_id,
            kind=data.get('kind', Reservation.Kind.RESERVATION),
            name=data.get('name', ''),
            preferred_datetime=data.get('preferred_datetime', ''),
            detail=data.get('detail', ''),
            phone=data.get('phone', ''),
            status=Reservation.Status.CONFIRMED,
        )
        return '受付を完了しました。担当スタッフが確認してご連絡いたします。'

    def _is_cancel(self, text):
        lowered = (text or '').strip().lower()
        return any(k in lowered for k in CANCEL_KEYWORDS)
