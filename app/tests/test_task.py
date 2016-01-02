from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User

from app.models import UserProfile
from app import tasks


class TaskTests(TestCase):

    def setUp(self):
        self.get_frontpaged_streamer_patch = mock.patch("app.tasks.get_frontpaged_streamer")
        self.get_frontpaged_streamer = self.get_frontpaged_streamer_patch.start()

    def tearDown(self):
        self.get_frontpaged_streamer_patch.stop()

    def _create_local_streamer_account(self, localusername, livetvusername, active=True, frontpaged=False):
        user = User.objects.create(username=localusername)
        profile = UserProfile.objects.get(user=user)
        profile.livetvusername = livetvusername
        profile.verified = True
        profile.active = active
        profile.frontpaged = frontpaged
        profile.save()
        return profile

    def test_set_frontpaged_user_will_mark_frontpaged_user_that_is_not_frontpaged_as_frontpaged(self):
        self.get_frontpaged_streamer.return_value = "taddeimania"
        self._create_local_streamer_account("taddeimania", "taddeimania")
        self._create_local_streamer_account("bobzoom", "BoBzoom")

        tasks.set_frontpaged_user(["taddeimania", "BoBzoom"])

        active_streamers = UserProfile.objects.filter(frontpaged=True)
        self.assertEqual(active_streamers.count(), 1)
        self.assertEqual(active_streamers[0].livetvusername, "taddeimania")

    def test_set_frontpaged_user_will_keep_frontpaged_user_that_is_still_frontpaged_as_frontpaged(self):
        self.get_frontpaged_streamer.return_value = "taddeimania"
        self._create_local_streamer_account("taddeimania", "taddeimania", frontpaged=True)
        self._create_local_streamer_account("bobzoom", "BoBzoom")

        tasks.set_frontpaged_user(["taddeimania", "BoBzoom"])

        active_streamers = UserProfile.objects.filter(frontpaged=True)
        self.assertEqual(active_streamers.count(), 1)
        self.assertEqual(active_streamers[0].livetvusername, "taddeimania")

    def test_set_frontpaged_user_will_turn_frontpaged_user_false_if_that_user_is_no_longer_frontpaged(self):
        self.get_frontpaged_streamer.return_value = "heyitsleo"
        self._create_local_streamer_account("taddeimania", "taddeimania", frontpaged=True)
        self._create_local_streamer_account("bobzoom", "BoBzoom")

        tasks.set_frontpaged_user(["taddeimania", "BoBzoom"])

        active_streamers = UserProfile.objects.filter(frontpaged=True)
        self.assertEqual(active_streamers.count(), 0)
