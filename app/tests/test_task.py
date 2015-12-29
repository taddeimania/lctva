from unittest import mock

from django.test import TestCase
from django.contrib.auth.models import User

from app.models import UserProfile
from app import tasks


class TaskTests(TestCase):

    def setUp(self):
        self.external_patch = mock.patch("app.tasks.get_current_stream_usernames")
        self.get_current_stream_usernames = self.external_patch.start()

    def tearDown(self):
        self.external_patch.stop()

    def _create_local_streamer_account(self, localusername, livetvusername, active=True):
        user = User.objects.create(username=localusername)
        profile = UserProfile.objects.get(user=user)
        profile.livetvusername = livetvusername
        profile.verified = True
        profile.active = active
        profile.save()
        return profile

    def test_get_verified_usernames_returns_verified_usernames_as_is(self):
        user_one = User.objects.create(username="blah")
        user_two = User.objects.create(username="blahblah")

        profile_one = UserProfile.objects.get(user=user_one)
        profile_one.livetvusername = "BlahBlahLolWhat"
        profile_one.verified = True
        profile_one.save()

        profile_two = UserProfile.objects.get(user=user_two)
        profile_two.livetvusername = "wwwwwXxXU"
        profile_two.verified = True
        profile_two.save()
        users = tasks.get_verified_usernames()
        self.assertEqual(users, {'BlahBlahLolWhat', 'wwwwwXxXU'})

    def test_check_streamers_will_mark_active_streamers_who_arent_streaming_anymore_as_not_active(self):
        self.get_current_stream_usernames.return_value = {"bobzoom"}
        self._create_local_streamer_account("taddeimania", "taddeimania")
        self._create_local_streamer_account("bobzoom", "BoBzoom")
        self._create_local_streamer_account("asdf", "asdf", active=False)
        active_streamers = UserProfile.objects.filter(active=True)
        self.assertEqual(active_streamers.count(), 2)

        # Run the task
        tasks.check_streamers()
        active_streamers = UserProfile.objects.filter(active=True)
        self.assertEqual(active_streamers.count(), 1)
        self.assertEqual(active_streamers[0].livetvusername, "BoBzoom")

    def test_check_streamers_will_mark_inactive_streamers_who_are_streaming_as_active(self):
        self.get_current_stream_usernames.return_value = {"bobzoom", "taddeimania"}
        self._create_local_streamer_account("taddeimania", "taddeimania", active=False)
        self._create_local_streamer_account("bobzoom", "BoBzoom")
        self._create_local_streamer_account("asdf", "asdf", active=False)
        active_streamers = UserProfile.objects.filter(active=True)
        self.assertEqual(active_streamers.count(), 1)

        # Run the task
        tasks.check_streamers()
        active_streamers = UserProfile.objects.filter(active=True)
        self.assertEqual(active_streamers.count(), 2)
        self.assertEqual(active_streamers[0].livetvusername, "taddeimania")
        self.assertEqual(active_streamers[1].livetvusername, "BoBzoom")
