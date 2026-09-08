from django.test import TestCase

from reservations.models import Reservation

from .intake import IntakeFlow


class IntakeFlowTests(TestCase):
    def setUp(self):
        self.flow = IntakeFlow('user-1')

    def tearDown(self):
        Reservation.objects.filter(user_id='user-1', status=Reservation.Status.PENDING).delete()

    def test_start_asks_name(self):
        reply = self.flow.start('修理の依頼をしたい')
        self.assertIn('お名前', reply)

    def test_full_flow_creates_reservation(self):
        self.flow.start('予約したい')
        self.flow.handle('田中')
        self.flow.handle('明日の午後3時')
        reply = self.flow.handle('点検')
        self.assertIn('電話番号', reply)
        reply = self.flow.handle('090-0000-0000')
        self.assertIn('完了', reply)
        self.assertEqual(Reservation.objects.count(), 1)
        r = Reservation.objects.get()
        self.assertEqual(r.name, '田中')
        self.assertEqual(r.status, Reservation.Status.CONFIRMED)

    def test_cancel_cancels_reservation(self):
        self.flow.start('予約したい')
        reply = self.flow.handle('キャンセル')
        self.assertIn('キャンセル', reply)
        r = Reservation.objects.get(user_id='user-1')
        self.assertEqual(r.status, Reservation.Status.CANCELLED)

    def test_repair_kind_detected(self):
        self.flow.start('修理の依頼をしたい')
        r = Reservation.objects.get(user_id='user-1', status=Reservation.Status.PENDING)
        self.assertEqual(r.kind, Reservation.Kind.REPAIR)

    def test_start_discards_previous_pending(self):
        self.flow.start('予約したい')
        self.flow.handle('田中')
        # 新しい予約を開始すると、受付中の前レコードは破棄される
        self.flow.start('予約したい')
        self.assertEqual(
            Reservation.objects.filter(user_id='user-1', status=Reservation.Status.PENDING).count(),
            1,
        )
