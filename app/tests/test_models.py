
from django.test import TestCase
from django.contrib.auth.models import User

from app.models import Notification


class NotificationModelTests(TestCase):

    def test_get_unread_notifications_will_only_return_notifications_a_user_is_not_related_to(self):
        user = User.objects.create(username="blah")
        unread_notification = Notification.objects.create(body="ASDF")
        read_notification = Notification.objects.create(body="ZXVV")
        read_notification.readers.add(user)
        results = Notification.objects.get_unread_notifications(user)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.get(), unread_notification)
