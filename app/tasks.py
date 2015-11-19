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


@app.task
def watch_viewers():
    url = "https://www.livecoding.tv/livestreams/{}/stats.json"
    for profile in UserProfile.objects.filter(active=True):
        Node.objects.create(
            current_total=get_viewer_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername)


@app.task
def check_streamers():
    for profile in UserProfile.objects.filter(active=True):
        if profile.is_user_currently_streaming and not profile.active:
            profile.active = True
            profile.save()
        elif not profile.is_user_currently_streaming and profile.active:
            profile.active = False
            profile.save()


@app.task
def check_friends():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )
