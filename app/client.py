
import requests
from collections import namedtuple

from app.models import ApiAccessToken


class LiveCodingClient:

    host = "https://www.livecoding.tv/api"

    def __init__(self, livetvusername):
        self.access = ApiAccessToken.objects.get(user__userprofile__livetvusername=livetvusername)
        self.headers = {
            'authorization': "Bearer {}".format(self.access.access_token),
            'cache-control': "no-cache",
            'postman-token': self.access.state
        }

    def _data_factory(self, name, data):
        return namedtuple(name, data.keys())(**data)

    def get_user_details(self):
        user_details = requests.get("{}/v1/user/".format(self.host), headers=self.headers).json()
        return self._data_factory("user", user_details)
