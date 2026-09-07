import re
from datetime import datetime

from django.db import models
from django.utils import timezone


class Store(models.Model):
    name = models.CharField('店舗名', max_length=100)
    business_hours = models.CharField('営業時間', max_length=255, blank=True)
    closed_days = models.CharField('定休日', max_length=255, blank=True)
    access = models.TextField('アクセス情報', blank=True)
    payment_methods = models.TextField('支払い方法', blank=True)
    phone = models.CharField('電話番号', max_length=20, blank=True)
    address = models.CharField('住所', max_length=255, blank=True)

    class Meta:
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return self.name

    def is_open_now(self, now=None):
        """現在の営業状態を判定する（定休日と営業時間を簡易判定）。"""
        now = now or timezone.localtime()
        return not self._is_closed_today(now) and self._is_within_hours(now)

    def _is_closed_today(self, now):
        if not self.closed_days:
            return False
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        today = weekdays[now.weekday()]
        return today in self.closed_days

    def _is_within_hours(self, now):
        if not self.business_hours:
            return True
        match = re.search(r'(\d{1,2}):(\d{2})\s*[-~〜]\s*(\d{1,2}):(\d{2})', self.business_hours)
        if not match:
            return True
        open_min = int(match.group(1)) * 60 + int(match.group(2))
        close_min = int(match.group(3)) * 60 + int(match.group(4))
        current_min = now.hour * 60 + now.minute
        return open_min <= current_min < close_min
