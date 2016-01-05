
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
        self.key = ApiKey.objects.get(provider="livecodingtv")
        self.headers = self._build_headers(self.access)

    @staticmethod
    def _build_headers(token):
        return {
            'authorization': "Bearer {}".format(token.access_token),
            'cache-control': "no-cache",
        }

    def _data_factory(self, name, data):
        return namedtuple(name, data.keys())(**data)

    def _make_request(self, url):
        request_url = "{}{}{}".format(self.host, self.version, url)
        response = requests.get(request_url, headers=self.headers)
        # if 401 (auth not provided, lets get a new token and retry?)
        if response.status_code == 401:
            self.access = LiveCodingAuthClient(
                code=self.access.access_code, refresh=True).get_auth_token(self.access.user)
            headers = self._build_headers(self.access)
            response = requests.get(request_url, headers=headers)
        self.key.increment()
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
        stream_details = requests.get(
            "{}/v1/livestreams/{}/".format(self.host, self.livetvusername), headers=self.headers).json()
        return self._data_factory("stream", stream_details)

    def get_onair_streams(self):
        stream_details = self._make_request("/livestreams/onair/")
        return self._data_factory("stream", stream_details)

    def _get_more_videos(self, stream_details):
        get_videos = lambda self, stream_details: [self._data_factory("video", video) for video in stream_details["results"]]
        yield get_videos(self, stream_details)
        while stream_details["next"]:
            next_params = stream_details["next"][stream_details["next"].index("?"):]
            stream_details = self._make_request("/videos/{}".format(next_params))
            yield get_videos(self, stream_details)

    def get_all_videos(self):
        stream_details = self._make_request("/videos/")
        if not stream_details["next"]:
            return [self._data_factory("video", video) for video in stream_details["results"]]

        return self._get_more_videos(stream_details)


class LiveCodingAuthClient:

    auth_url = "https://www.livecoding.tv/o/token/"
    payload_body = "code={}&grant_type={}&redirect_uri={}&client_id={}&client_secret={}"

    def __init__(self, code, refresh=False):
        self.refresh = refresh
        self.code = code
        self.key = ApiKey.objects.get(provider="livecodingtv")
        self.basic_auth_header_val = b64encode(str.encode("{}:{}".format(self.key.client_id, self.key.client_secret)))
        self.payload = self.payload_body.format(
            code,
            "authorization_code",
            self.key.redirect_url,
            self.key.client_id,
            self.key.client_secret
        )
        self.headers = {
            'authorization': "Basic " + self.basic_auth_header_val.decode("utf-8"),
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded"
        }

    def get_auth_token(self, user):
        payload = self.payload
        if self.refresh:
            token = ApiAccessToken.objects.get(user=user)
            payload_body = "grant_type={}&redirect_uri={}&client_id={}&client_secret={}"
            payload = payload_body.format(
                "refresh_token",
                self.key.redirect_url,
                self.key.client_id,
                self.key.client_secret
            ) + "&refresh_token={}".format(token.refresh_token)
        response = requests.post(self.auth_url, data=payload, headers=self.headers).json()
        token, _ = ApiAccessToken.objects.get_or_create(user=user)
        token.access_code = self.code
        token.access_token = response['access_token']
        token.refresh_token = response['refresh_token']
        token.save()
        return token
