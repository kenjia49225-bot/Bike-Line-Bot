from django.test import TestCase

from .models import Reservation


class ReservationModelTests(TestCase):
    def test_create_reservation(self):
        r = Reservation.objects.create(
            user_id='user-1',
            kind=Reservation.Kind.RESERVATION,
            name='田中',
            preferred_datetime='明日の午後3時',
            detail='点検',
            phone='090-0000-0000',
        )
        self.assertEqual(r.user_id, 'user-1')
        self.assertEqual(r.status, Reservation.Status.PENDING)
        self.assertEqual(str(r), 'user-1 (予約)')

    def test_default_kind_reservation(self):
        r = Reservation.objects.create(user_id='user-2')
        self.assertEqual(r.kind, Reservation.Kind.RESERVATION)

    def test_cancel_status(self):
        r = Reservation.objects.create(user_id='user-3', status=Reservation.Status.CANCELLED)
        self.assertEqual(r.get_status_display(), 'キャンセル')
