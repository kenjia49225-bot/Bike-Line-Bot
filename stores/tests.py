from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Store


class StoreModelTests(TestCase):
    def test_create_store(self):
        store = Store.objects.create(
            name='テスト店舗',
            business_hours='10:00-19:00',
            closed_days='水曜日',
            access='駅から徒歩5分',
            payment_methods='現金、クレジットカード',
            phone='03-1234-5678',
            address='東京都新宿区1-1-1',
        )
        self.assertEqual(store.name, 'テスト店舗')
        self.assertEqual(str(store), 'テスト店舗')
        self.assertEqual(Store.objects.count(), 1)

    def test_optional_fields_blank(self):
        store = Store.objects.create(name='店舗名のみ')
        self.assertEqual(store.business_hours, '')
        self.assertEqual(store.closed_days, '')
        self.assertEqual(store.access, '')
        self.assertEqual(store.payment_methods, '')
        self.assertEqual(store.phone, '')
        self.assertEqual(store.address, '')


class StoreOpenNowTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name='営業判定テスト店舗',
            business_hours='10:00-19:00',
            closed_days='水曜日',
        )

    def test_open_within_hours_on_weekday(self):
        now = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.get_current_timezone())  # 火曜 12:00
        self.assertTrue(self.store.is_open_now(now))

    def test_closed_outside_hours(self):
        now = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.get_current_timezone())  # 火曜 20:00
        self.assertFalse(self.store.is_open_now(now))

    def test_closed_on_closed_day(self):
        now = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.get_current_timezone())  # 水曜 12:00
        self.assertFalse(self.store.is_open_now(now))
