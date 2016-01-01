
import requests
from base64 import b64encode
from collections import namedtuple

from app.models import ApiAccessToken, ApiKey


class LiveCodingClient:

    host = "https://www.livecoding.tv/api"
    version = "/v1"

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

    def _make_request(self, url):
        request_url = "{}{}{}".format(self.host, self.version, url)
        response = requests.get(request_url, headers=self.headers)
        # if 401 (auth not provided, lets get a new token and retry?)
        if response.status_code == 401:
            self.access = LiveCodingAuthClient(code=self.access.access_code).get_auth_token(self.access.user)
            response = requests.get(request_url, headers=self.headers)
            print("REMADE TOKEN FROM RESPONSE: ", response)
        return response.json()

    @classmethod
    def get_user_from_token(cls, token):
        headers = cls._build_headers(token)
        data = requests.get("{}/v1/user/".format(cls.host), headers=headers).json()
        return namedtuple("user", data.keys())(**data)

    def get_user_details(self):
        user_details = self._make_request("/user/")
        return self._data_factory("user", user_details)

    def get_stream_details(self):
        # No permission with only 'read' scope
        stream_details = requests.get("{}/v1/livestreams/{}/".format(self.host, self.livetvusername), headers=self.headers).json()
        return self._data_factory("stream", stream_details)

    def get_onair_streams(self):
        stream_details = requests.get("{}/v1/livestreams/onair/".format(self.host), headers=self.headers).json()
        return self._data_factory("stream", stream_details)


class LiveCodingAuthClient:

    auth_url = "https://www.livecoding.tv/o/token/"

    def __init__(self, code):
        self.code = code
        self.key = ApiKey.objects.get(provider="livecodingtv")
        self.basic_auth_header_val = b64encode(str.encode("{}:{}".format(self.key.client_id, self.key.client_secret)))
        self.payload = "code={}&grant_type=authorization_code&redirect_uri={}&client_id={}&client_secret={}".format(
            code,
            self.key.redirect_url,
            self.key.client_id,
            self.key.client_secret
        )
        self.headers = {
            'authorization': "Basic " + self.basic_auth_header_val.decode("utf-8"),
            'cache-control': "no-cache",
            'postman-token': self.key.state,
            'content-type': "application/x-www-form-urlencoded"
        }

    def get_auth_token(self, user):
        response = requests.post(self.auth_url, data=self.payload, headers=self.headers).json()
        print(response)
        ApiAccessToken.objects.filter(user=user).delete()
        return ApiAccessToken.objects.create(
            user=user,
            access_code=self.code,
            access_token=response['access_token'],
            refresh_token=response['refresh_token'])
