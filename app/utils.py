
import datetime
from collections import namedtuple, OrderedDict
from statistics import mean


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


def adjust_time(timestamp):
    return timestamp - datetime.timedelta(hours=5)


def prepare_data_for_plot(nodes):
    return [(adjust_time(node[0]).strftime("%Y-%m-%d %H:%M:%S"), node[1])
            for node in nodes]
