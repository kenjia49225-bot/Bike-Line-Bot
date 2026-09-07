from django.db import models


class FAQ(models.Model):
    question = models.TextField('質問文')
    answer = models.TextField('回答文')
    is_active = models.BooleanField('公開状態', default=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['-created_at']

    def __str__(self):
        return self.question
