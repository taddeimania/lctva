
import requests
from collections import namedtuple

from app.models import ApiAccessToken


class LiveCodingClient:

    host = "https://www.livecoding.tv/api"

    def __init__(self, livetvusername):
        self.livetvusername = livetvusername
        self.access = ApiAccessToken.objects.get(user__userprofile__livetvusername=livetvusername)
        self.headers = self._build_headers(self.access)

    @staticmethod
    def _build_headers(token):
        return {
            'authorization': "Bearer {}".format(token.access_token),
            'cache-control': "no-cache",
            'postman-token': token.state
        }

    def _data_factory(self, name, data):
        return namedtuple(name, data.keys())(**data)

    @classmethod
    def get_user_from_token(cls, token):
        headers = cls._build_headers(token)
        data = requests.get("{}/v1/user/".format(cls.host), headers=headers).json()
        return namedtuple("user", data.keys())(**data)

    def get_user_details(self):
        user_details = requests.get("{}/v1/user/".format(self.host), headers=self.headers).json()
        return self._data_factory("user", user_details)

    def get_stream_details(self):
        # No permission with only 'read' scope
        stream_details = requests.get("{}/v1/livestreams/{}/".format(self.host, self.livetvusername), headers=self.headers).json()
        return self._data_factory("stream", stream_details)

    def get_onair_streams(self):
        stream_details = requests.get("{}/v1/livestreams/onair/".format(self.host), headers=self.headers).json()
        return self._data_factory("stream", stream_details)
