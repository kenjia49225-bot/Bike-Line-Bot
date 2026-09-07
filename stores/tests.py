from django.test import TestCase

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
