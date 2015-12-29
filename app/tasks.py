import requests
from bs4 import BeautifulSoup

from watcher.celery import app
from app.models import Node, UserProfile, Friends
from app.utils import clean_usernames


def get_viewer_count(username, url):
    data = requests.get(url.format(username).lower()).json()
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
    return set(UserProfile.objects.filter(verified=True).values_list("livetvusername", flat=True))


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
    cleaned_usernames = clean_usernames(verified_usernames)
    current_streamers = get_current_stream_usernames()  # scraped from livecoding.tv

    to_activate_usernames = [username for username in verified_usernames
                             if username.lower() in cleaned_usernames.intersection(current_streamers)]
    to_deactivate_usernames = [username for username in verified_usernames
                               if username.lower() in cleaned_usernames.difference(current_streamers)]

    UserProfile.objects.filter(livetvusername__in=to_activate_usernames, active=False).update(active=True)
    UserProfile.objects.filter(livetvusername__in=to_deactivate_usernames, active=True).update(active=False)


@app.task
def check_friends():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )
