import datetime
from statistics import mean

from app.client import LiveCodingClient
from app.models import Node, UserProfile, Friends, Viewers, ApiKey, Leader, DailyLeaderboard
from app.utils import clean_usernames, unzip_data, LeaderBoardGenerator
from watcher.celery import app

from bs4 import BeautifulSoup
from django.utils import timezone as django_timezone
import requests


def get_verified_usernames():
    return set(UserProfile.objects.all().values_list("livetvusername", flat=True))


def get_frontpaged_streamer():
    body = requests.get("https://www.livecoding.tv/").content
    souper = BeautifulSoup(body, "html.parser")
    return souper.find("h2", {"class": "video-home-stream--title"}).find('span').text


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
    set_frontpaged_user(get_verified_usernames())


def get_friend_count(username, url):
    data = requests.get(url.format(username)).content
    souper = BeautifulSoup(data, 'html.parser')
    return int(souper.find("span", id="followers_count").text)


@app.task
def check_friends_and_total_viewers():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.all():
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )


@app.task
def send_email(to_name, to_address, subject, text):
    # Usage:
    # send_email.delay("Joel Taddei", "jtaddei@gmail.com", "Put Subject Here", "Body of message")
    key = ApiKey.objects.get(provider="mailgun")
    return requests.post(
        key.redirect_url,
        auth=("api", key.client_secret),
        data={"from": "LCTVA <noreply@lctva.joel.io>",
              "to": "{} <{}>".format(to_name, to_address),
              "subject": subject,
              "text": text})


@app.task
def create_daily_leaderboard():
    yesterday = (django_timezone.now() + datetime.timedelta(days=-1)).date()
    yesterday_nodes = Node.objects.filter(timestamp__contains=yesterday)
    users = set(yesterday_nodes.values_list("livetvusername", flat=True))
    # Clean outliers from node table
    for user in users:
        to_clean_nodes = yesterday_nodes.filter(livetvusername=user)
        Node.objects.find_outliers(to_clean_nodes).delete()

    yesterday_nodes = Node.objects.filter(timestamp__contains=yesterday)
    leaderboard = DailyLeaderboard.objects.create(date=yesterday)
    lb_gen = LeaderBoardGenerator(yesterday_nodes)
    leaderboard_data = lb_gen.get_data()
    for minute_leader in leaderboard_data["minutes_streamed"]:
        leader = Leader.objects.create(
            livetvusername=minute_leader[1],
            minutes=minute_leader[0]
        )
        leaderboard.minutes_leaders.add(leader)
    for viewer_leader in leaderboard_data["average_viewers"]:
        leader = Leader.objects.create(
            livetvusername=viewer_leader[1],
            minutes=viewer_leader[0]
        )
        leaderboard.viewers_leaders.add(leader)
