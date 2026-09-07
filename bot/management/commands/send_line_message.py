from django.core.management.base import BaseCommand, CommandError

from bot.services import push_message
from conversations.models import Conversation


class Command(BaseCommand):
    help = '指定ユーザーへ LINE プッシュメッセージを送信する（人間からの返信など）'

    def add_arguments(self, parser):
        parser.add_argument('user_id', help='送信先の LINE ユーザーID')
        parser.add_argument('text', help='送信するメッセージ本文')

    def handle(self, *args, **options):
        user_id = options['user_id']
        text = options['text']
        try:
            sent = push_message(user_id, text)
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f'送信に失敗しました: {exc}') from exc

        if not sent:
            raise CommandError('LINE_CHANNEL_ACCESS_TOKEN が設定されていません。')

        Conversation.objects.create(
            user_id=user_id,
            role=Conversation.Role.BOT,
            content=text,
            status=Conversation.Status.RESOLVED,
        )
        self.stdout.write(self.style.SUCCESS(f'送信完了: {user_id}'))
