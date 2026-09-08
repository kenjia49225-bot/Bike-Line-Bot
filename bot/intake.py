from reservations.models import Reservation

CANCEL_KEYWORDS = ('キャンセル', 'やめる', '中止', 'cancel')

# STEPS の順序。kind は開始時に確定するため、以降の入力ステップを列挙する。
FIELD_STEPS = ('name', 'preferred_datetime', 'detail', 'phone')

PROMPTS = {
    'name': 'お名前を入力してください。',
    'preferred_datetime': '希望日時を入力してください（例: 明日の午後3時）。',
    'detail': '内容を入力してください。',
    'phone': '電話番号を入力してください（任意）。「なし」でも構いません。',
}


class IntakeFlow:
    """予約・修理受付の段階的入力フロー（状態は DB に保存し複数ワーカーで共有）。"""

    def __init__(self, user_id):
        self.user_id = user_id

    def start(self, text=''):
        """受付を開始して名前入力を求める。既存の受付中レコードがあれば破棄して作り直す。"""
        Reservation.objects.filter(
            user_id=self.user_id,
            status=Reservation.Status.PENDING,
        ).delete()

        reservation = Reservation.objects.create(
            user_id=self.user_id,
            kind=self._detect_kind(text),
            step='name',
            status=Reservation.Status.PENDING,
        )
        return PROMPTS['name']

    def handle(self, text):
        """入力を受け取り、次のプロンプトまたは完了メッセージを返す。"""
        if self._is_cancel(text):
            Reservation.objects.filter(
                user_id=self.user_id,
                status=Reservation.Status.PENDING,
            ).update(status=Reservation.Status.CANCELLED)
            return '受付をキャンセルしました。'

        reservation = Reservation.objects.filter(
            user_id=self.user_id,
            status=Reservation.Status.PENDING,
        ).first()

        if reservation is None:
            # 状態が無い場合は受付を開始
            return self.start(text)

        step = reservation.step
        if step not in FIELD_STEPS:
            return self.start(text)

        setattr(reservation, step, text)

        next_step = self._next_step(step)
        if next_step is None:
            reservation.step = ''
            reservation.status = Reservation.Status.CONFIRMED
            reservation.save()
            return '受付を完了しました。担当スタッフが確認してご連絡いたします。'

        reservation.step = next_step
        reservation.save()
        return PROMPTS[next_step]

    def _next_step(self, step):
        try:
            return FIELD_STEPS[FIELD_STEPS.index(step) + 1]
        except IndexError:
            return None

    def _detect_kind(self, text):
        if any(k in (text or '') for k in ('修理', '直して', '故障')):
            return Reservation.Kind.REPAIR
        return Reservation.Kind.RESERVATION

    def _is_cancel(self, text):
        lowered = (text or '').strip().lower()
        return any(k in lowered for k in CANCEL_KEYWORDS)
