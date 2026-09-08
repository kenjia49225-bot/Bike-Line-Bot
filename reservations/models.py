from django.db import models


class Reservation(models.Model):
    class Kind(models.TextChoices):
        RESERVATION = 'reservation', '予約'
        REPAIR = 'repair', '修理受付'

    class Status(models.TextChoices):
        PENDING = 'pending', '受付中'
        CONFIRMED = 'confirmed', '確定待ち'
        DONE = 'done', '確定済み'
        CANCELLED = 'cancelled', 'キャンセル'

    user_id = models.CharField('ユーザー識別子', max_length=255)
    kind = models.CharField('種別', max_length=20, choices=Kind.choices, default=Kind.RESERVATION)
    name = models.CharField('お名前', max_length=100, blank=True)
    preferred_datetime = models.CharField('希望日時', max_length=255, blank=True)
    detail = models.TextField('内容', blank=True)
    phone = models.CharField('電話番号', max_length=20, blank=True)
    status = models.CharField('ステータス', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '予約・修理受付'
        verbose_name_plural = '予約・修理受付'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} ({self.get_kind_display()})'
