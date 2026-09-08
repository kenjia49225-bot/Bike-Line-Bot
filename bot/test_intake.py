from django.test import TestCase

from reservations.models import Reservation

from .intake import IntakeFlow


class IntakeFlowTests(TestCase):
    def setUp(self):
        self.flow = IntakeFlow('user-1')
        self.flow.clear()

    def tearDown(self):
        self.flow.clear()

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

    def test_cancel_clears_flow(self):
        self.flow.start('予約したい')
        reply = self.flow.handle('キャンセル')
        self.assertIn('キャンセル', reply)
        self.assertEqual(Reservation.objects.count(), 0)
