from django.db import models


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
