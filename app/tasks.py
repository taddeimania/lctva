import datetime
from statistics import mean

from app.client import LiveCodingClient
from app.models import Node, UserProfile, Friends, Viewers, ApiKey, Leader, Leaderboard
from app.utils import clean_usernames, unzip_data, LeaderBoardGenerator
from watcher.celery import app

from bs4 import BeautifulSoup
from django.utils import timezone as django_timezone
import requests


def legacy_get_viewer_count(username, url):
    return _get_count(username, url, "views_live")


@app.task
def legacy_watch_viewers():
    url = "https://www.livecoding.tv/livestreams/{}/stats.json"
    # total_streamers = sum([stream["viewers_live"] for stream in LiveCodingClient("taddeimania").get_onair_streams().results])
    for profile in UserProfile.objects.filter(active=True):
        viewer_count = legacy_get_viewer_count(profile.livetvusername, url)
        print(profile)
        print(viewer_count)
        Node.objects.create(
            current_total=viewer_count,
            total_site_streamers=1,
            livetvusername=profile.livetvusername)


def get_current_stream_usernames():
    body = requests.get("https://www.livecoding.tv/livestreams/").content
    souper = BeautifulSoup(body, "html.parser")
    return {element.text.strip().lower() for element in souper.findAll("span", {"class": "browse-main-videos--username"})}


def get_verified_usernames():
    return set(UserProfile.objects.filter(verified=True).values_list("livetvusername", flat=True))


@app.task
def legacy_check_streamers():
    verified_usernames = get_verified_usernames()
    cleaned_usernames = clean_usernames(verified_usernames)
    current_streamers = get_current_stream_usernames()  # scraped from livecoding.tv

    to_activate_usernames = [username for username in verified_usernames
                             if username.lower() in cleaned_usernames.intersection(current_streamers)]
    to_deactivate_usernames = [username for username in verified_usernames
                               if username.lower() in cleaned_usernames.difference(current_streamers)]

    UserProfile.objects.filter(livetvusername__in=to_activate_usernames, active=False).update(active=True)
    UserProfile.objects.filter(livetvusername__in=to_deactivate_usernames, active=True).update(active=False)
    set_frontpaged_user(verified_usernames)


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


def get_friend_count(username, url):
    data = requests.get(url.format(username)).content
    souper = BeautifulSoup(data, 'html.parser')
    return int(souper.find("span", id="followers_count").text)


def _get_count(username, url, field):
    data = requests.get(url.format(username).lower()).json()
    return int(data.get(field))


def get_total_viewer_count(username, url):
    return _get_count(username, url, "views_overall")


@app.task
def check_friends_and_total_viewers():
    url = "https://www.livecoding.tv/{}/"
    for profile in UserProfile.objects.filter(verified=True):
        Friends.objects.create(
            current_total=get_friend_count(profile.livetvusername, url),
            livetvusername=profile.livetvusername
        )
        # Viewers.objects.create(
        #     current_total=get_total_viewer_count(profile.livetvusername, url),
        #     livetvusername=profile.livetvusername
        # )


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


def get_today():
    return datetime.date.today()


# def lower_resolution():
#     today = get_today()
#     yesterday = today + datetime.timedelta(days=-1)
#     old_data = Node.objects.filter(timestamp__gte=yesterday).values_list('livetvusername', 'current_total')
#     data_x, data_y = unzip_data(old_data)
#     unique_users = set(data_x)


def create_daily_leaderboard():
    yesterday = (django_timezone.now() + datetime.timedelta(days=-1)).date()
    leaderboard = Leaderboard.objects.create(date=yesterday)
    yesterday_nodes = Node.objects.filter(timestamp__contains=yesterday)
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
