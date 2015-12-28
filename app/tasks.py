import requests
from bs4 import BeautifulSoup

from watcher.celery import app
from app.models import Node, UserProfile, Friends


def get_viewer_count(username, url):
    data = requests.get(url.format(username)).json()
    return int(data.get("views_live"))


def get_friend_count(username, url):
    data = requests.get(url.format(username)).content
    souper = BeautifulSoup(data, 'html.parser')
    return int(souper.find("span", id="followers_count").text)


def get_current_stream_usernames():
    body = requests.get("https://www.livecoding.tv/livestreams/").content
    souper = BeautifulSoup(body, "html.parser")
    return {element.text.strip().lower() for element in souper.findAll("span", {"class": "browse-main-videos--username"})}


def get_verified_usernames():
    return set(map(str.lower, UserProfile.objects.filter(verified=True).values_list("livetvusername", flat=True)))


@app.task
def watch_viewers():
    url = "https://www.livecoding.tv/livestreams/{}/stats.json"
    for profile in UserProfile.objects.filter(active=True):
        Node.objects.create(
            current_total=get_viewer_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername)


@app.task
def check_streamers():
    verified_usernames = get_verified_usernames()
    current_streamers = get_current_stream_usernames()
    inter = verified_usernames.intersection(current_streamers)
    outer = verified_usernames.difference(current_streamers)
    # VV Set non-active flagged streamers that are streaming as active
    UserProfile.objects.filter(livetvusername__in=inter, active=False).update(active=True)
    UserProfile.objects.filter(livetvusername__in=outer, active=True).update(active=False)
    # get a list of all current stream account names
    # get a list of all current registered lctva streamer account names
    # get intersection and mark all users as active
    # get difference and mark all registered lctva users as inactive
    # for profile in UserProfile.objects.filter(active=True):
    #     if profile.is_user_currently_streaming and not profile.active:
    #         profile.active = True
    #         profile.save()
    #     elif not profile.is_user_currently_streaming and profile.active:
    #         profile.active = False
    #         profile.save()


@app.task
def check_friends():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )
