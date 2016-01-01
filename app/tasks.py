import requests
from bs4 import BeautifulSoup

from watcher.celery import app
from app.models import Node, UserProfile, Friends, Viewers, ApiAccessToken
from app.utils import clean_usernames
from app.client import LiveCodingClient


def _get_count(username, url, field):
    data = requests.get(url.format(username).lower()).json()
    return int(data.get(field))


def get_total_viewer_count(username, url):
    return _get_count(username, url, "views_overall")


def get_friend_count(username, url):
    data = requests.get(url.format(username)).content
    souper = BeautifulSoup(data, 'html.parser')
    return int(souper.find("span", id="followers_count").text)


def get_current_stream_usernames():
    body = requests.get("https://www.livecoding.tv/livestreams/").content
    souper = BeautifulSoup(body, "html.parser")
    return {element.text.strip().lower() for element in souper.findAll("span", {"class": "browse-main-videos--username"})}


def get_frontpaged_streamer():
    body = requests.get("https://www.livecoding.tv/").content
    souper = BeautifulSoup(body, "html.parser")
    return souper.find("h2", {"class": "video-home-stream--title"}).find('span').text


@app.task
def watch_viewers():
    streams = LiveCodingClient("taddeimania").get_onair_streams().results
    streamers = dict([(stream['user__slug'], stream['viewers_live']) for stream in streams])
    total_viewers = sum(streamers.values())
    for livetvusername in streamers.keys():
        viewer_count = streamers[livetvusername]
        Node.objects.create(
            current_total=viewer_count,
            total_site_streamers=total_viewers,
            livetvusername=livetvusername)


def set_frontpaged_user(verified_usernames):
    frontpaged_streamer = get_frontpaged_streamer()
    if frontpaged_streamer in verified_usernames:
        still_frontpaged = UserProfile.objects.filter(livetvusername=frontpaged_streamer, frontpaged=True)
        if not still_frontpaged:
            UserProfile.objects.filter(frontpaged=True).update(frontpaged=False)
            user = UserProfile.objects.get(livetvusername=frontpaged_streamer)
            user.frontpaged = True
            user.save()
    else:
        UserProfile.objects.filter(frontpaged=True).update(frontpaged=False)


@app.task
def check_friends():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )


@app.task
def check_total_viewers():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Viewers.objects.create(
            current_total=get_total_viewer_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )
