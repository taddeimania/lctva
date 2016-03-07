import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from app.models import Node


class OnlineViewTests(TestCase):

    def test_user_online_view_returns_json_true_if_user_has_node_within_last_30_sec(self):
        past = datetime.datetime.now() - datetime.timedelta(seconds=29)
        Node.objects.create(livetvusername="taddeimania", current_total=3, total_site_streamers=0, timestamp=past)
        response = self.client.get(reverse("user_online_view", kwargs={"username": "taddeimania"}))
        self.assertEqual(response.json(), True)

    def test_user_online_view_returns_json_false_if_user_has_node_within_last_31_sec(self):
        past = datetime.datetime.now() - datetime.timedelta(seconds=31)
        Node.objects.create(livetvusername="taddeimania", current_total=3, total_site_streamers=0, timestamp=past)
        response = self.client.get(reverse("user_online_view", kwargs={"username": "taddeimania"}))
        self.assertEqual(response.json(), False)

    def test_user_online_view_returns_json_false_if_no_user_nodes_in_a_while(self):
        response = self.client.get(reverse("user_online_view", kwargs={"username": "taddeimania"}))
        self.assertEqual(response.json(), False)
