
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
