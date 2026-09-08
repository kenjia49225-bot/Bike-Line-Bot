from django.db import models


class RateLimit(models.Model):
    """ユーザー単位のレート制限カウンタ（複数ワーカーで共有するため DB に保存）。"""

    user_id = models.CharField('ユーザー識別子', max_length=255, unique=True)
    count = models.IntegerField('カウント', default=0)
    window_start = models.DateTimeField('ウィンドウ開始日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'レート制限'
        verbose_name_plural = 'レート制限'

    def __str__(self):
        return f'{self.user_id} ({self.count})'
