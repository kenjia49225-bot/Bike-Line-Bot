from unittest import mock

from django.test import TestCase

from .notifications import _staff_ids, notify_staff_handoff


class NotificationsTests(TestCase):
    def test_staff_ids_empty_by_default(self):
        self.assertEqual(_staff_ids(), [])

    def test_staff_ids_parsed(self):
        with self.settings(STAFF_LINE_USER_IDS='staff-1, staff-2 ,staff-3'):
            self.assertEqual(_staff_ids(), ['staff-1', 'staff-2', 'staff-3'])

    @mock.patch('bot.notifications.push_message')
    def test_notify_skips_when_no_staff(self, mock_push):
        count = notify_staff_handoff('user-1', '質問です')
        self.assertEqual(count, 0)
        mock_push.assert_not_called()

    @mock.patch('bot.notifications.push_message')
    def test_notify_sends_to_all_staff(self, mock_push):
        mock_push.return_value = True
        with self.settings(STAFF_LINE_USER_IDS='staff-1,staff-2'):
            count = notify_staff_handoff('user-1', '質問です')
        self.assertEqual(count, 2)
        self.assertEqual(mock_push.call_count, 2)
