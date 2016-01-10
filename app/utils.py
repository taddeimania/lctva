
import datetime
from collections import namedtuple, OrderedDict
from statistics import mean

from pytz import timezone


def daily_aggregator(queryset):
    aggregated_collection = OrderedDict()
    day_stats = namedtuple("day_stats", ["day", "mean", "max", "minutes"])
    for result in queryset.order_by("-timestamp"):
        day = result.timestamp.date().strftime("%Y-%m-%d")
        if day in aggregated_collection.keys():
            aggregated_collection[day].append(result.current_total)
        else:
            aggregated_collection[day] = []
            aggregated_collection[day].append(result.current_total)
    return [day_stats(date_str, round(mean(values), 2), max(values), round(len(values) * 5 / 60, 2))
            for date_str, values in aggregated_collection.items()]


def trending(data):
    if len(data) < 5:
        return False
    half = len(data) // 2 + 1
    return mean(data[half:]) > mean(data[:half])


def unzip_data(data):
    return [[node[_] for node in data] for _ in range(len(data[0]))]


def clean_usernames(usernames):
    return set(map(str.lower, usernames))


def adjust_time(timestamp, tz):
    return timestamp.astimezone(timezone(tz))


def prepare_data_for_plot(nodes, user):
    from app.models import UserProfile
    try:
        tz = UserProfile.objects.get(livetvusername=user).tz
    except UserProfile.DoesNotExist:
        tz = "America/New_York"

    return [(adjust_time(node[0], tz).strftime("%Y-%m-%d %H:%M:%S"), node[1])
            for node in nodes]


class LeaderBoardGenerator:

    def __init__(self, nodes):
        self.node_data = nodes.values_list("livetvusername", "timestamp", "current_total")

    def _minutes_streamed(self, counts):
        return round((counts / 60) * 5, 2)

    def _average_viewers(self, counts):
        return round(sum(counts) / len(counts))

    def get_data(self):
        leaderboard_data = {}
        user_set = {data[0] for data in self.node_data}
        user_minutes = []
        viewer_counts = []
        for user in user_set:
            user_data = list(filter(lambda x: x[0] == user, self.node_data))
            username, timestamps, values = unzip_data(user_data)
            user_minutes.append((self._minutes_streamed(len(values)), user))
            viewer_counts.append((self._average_viewers(values), user))

        leaderboard_data["minutes_streamed"] = sorted(user_minutes, reverse=True)[:10]
        leaderboard_data["average_viewers"] = sorted(viewer_counts, reverse=True)[:10]
        return leaderboard_data
