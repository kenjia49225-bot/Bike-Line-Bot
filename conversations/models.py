from django.db import models


class Conversation(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'ユーザー'
        BOT = 'bot', 'ボット'

    class Status(models.TextChoices):
        OPEN = 'open', '未対応'
        HANDOFF = 'handoff', '要引き継ぎ'
        RESOLVED = 'resolved', '解決済み'

    user_id = models.CharField('ユーザー識別子', max_length=255)
    role = models.CharField('発言者', max_length=10, choices=Role.choices)
    content = models.TextField('メッセージ内容')
    needs_human = models.BooleanField('要引き継ぎ', default=False)
    status = models.CharField('対応状況', max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = '会話履歴'
        verbose_name_plural = '会話履歴'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} ({self.role}): {self.content[:30]}'
