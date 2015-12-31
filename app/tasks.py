import requests
from bs4 import BeautifulSoup

from watcher.celery import app
from app.models import Node, UserProfile, Friends, Viewers, ApiAccessToken
from app.utils import clean_usernames
from app.client import LiveCodingClient


def _get_count(username, url, field):
    data = requests.get(url.format(username).lower()).json()
    return int(data.get(field))


def get_viewer_count(username, url):
    try:
        return LiveCodingClient(username).get_stream_details().viewers_live
    except ApiAccessToken.DoesNotExist:
        return _get_count(username, url, "views_live")


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


def get_verified_usernames():
    return set(UserProfile.objects.filter(verified=True).values_list("livetvusername", flat=True))


def get_frontpaged_streamer():
    body = requests.get("https://www.livecoding.tv/").content
    souper = BeautifulSoup(body, "html.parser")
    return souper.find("h2", {"class": "video-home-stream--title"}).find('span').text


@app.task
def watch_viewers():
    url = "https://www.livecoding.tv/livestreams/{}/stats.json"
    # total_streamers = sum([stream["viewers_live"] for stream in LiveCodingClient("taddeimania").get_onair_streams().results])
    for profile in UserProfile.objects.filter(active=True):
        viewer_count = get_viewer_count(profile.livetvusername, url)
        Node.objects.create(
            current_total=viewer_count,
            total_site_streamers=1,
            livetvusername=profile.livetvusername)


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
def check_streamers():
    verified_usernames = get_verified_usernames()
    cleaned_usernames = clean_usernames(verified_usernames)
    current_streamers = get_current_stream_usernames()  # scraped from livecoding.tv

    to_activate_usernames = [username for username in verified_usernames
                             if username.lower() in cleaned_usernames.intersection(current_streamers)]
    to_deactivate_usernames = [username for username in verified_usernames
                               if username.lower() in cleaned_usernames.difference(current_streamers)]

    UserProfile.objects.filter(livetvusername__in=to_activate_usernames, active=False).update(active=True)
    UserProfile.objects.filter(livetvusername__in=to_deactivate_usernames, active=True).update(active=False)

    set_frontpaged_user()


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
