
from django.test import TestCase
from django.contrib.auth.models import User

from app.models import Notification, Node


class NotificationModelTests(TestCase):

    def test_get_unread_notifications_will_only_return_notifications_a_user_is_not_related_to(self):
        user = User.objects.create(username="blah")
        unread_notification = Notification.objects.create(body="ASDF")
        read_notification = Notification.objects.create(body="ZXVV")
        read_notification.readers.add(user)
        results = Notification.objects.get_unread_notifications(user)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.get(), unread_notification)

    def test_notifications_are_defaul_ordered_by_descending_timestamp(self):
        first_notification = Notification.objects.create(body="ASDF")
        second_notification = Notification.objects.create(body="ZXVV")
        third_notification = Notification.objects.create(body="1234")

        results = Notification.objects.all()
        self.assertEqual(results.count(), 3)
        self.assertEqual(results.first(), third_notification)
        self.assertEqual(results[1], second_notification)
        self.assertEqual(results.last(), first_notification)


class NodeManagerTests(TestCase):

    def _create_node(self, username, current_total, total_viewers=1):
        return Node.objects.create(livetvusername=username, current_total=current_total, total_site_streamers=total_viewers)

    def test_find_outliers_will_return_nodes_from_a_qs_that_are_3_stdev_above_mean(self):
        # outlier upper limit is 57.76
        for _ in range(10):
            self._create_node("taddeimania", 10)
            self._create_node("taddeimania", 20)
            self._create_node("taddeimania", 12)
            self._create_node("taddeimania", 9)

        outlier = self._create_node("taddeimania", 58)
        outliers = Node.objects.find_outliers(Node.objects.filter(livetvusername="taddeimania"))
        self.assertEqual(outliers.count(), 1)
        self.assertEqual(outliers.get(), outlier)
