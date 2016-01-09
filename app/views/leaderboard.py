import datetime

from django.views.generic import TemplateView
from django.utils import timezone

from app.models import DailyLeaderboard


def get_daily_leaderboard_data(date):
    leaderboard = DailyLeaderboard.objects.filter(date=date)
    leaderboard_data = []
    if leaderboard:
        data = leaderboard.first()
        leaderboard_data = data
    yesterday = date + datetime.timedelta(days=-1)
    tomorrow = date + datetime.timedelta(days=1)
    return leaderboard_data, yesterday, tomorrow


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        date = timezone.now().date() + datetime.timedelta(days=-1)
        leaderboard_data, yesterday, tomorrow = get_daily_leaderboard_data(date)
        context["leaderboard_data"] = leaderboard_data
        context["yesterday"] = yesterday
        context["tomorrow"] = tomorrow
        return context



class LeaderBoardSpecificDayView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self, datestamp):
        context = super().get_context_data()
        date = datetime.datetime.strptime(datestamp, "%Y-%m-%d").date()
        leaderboard_data, yesterday, tomorrow = get_daily_leaderboard_data(date)
        context["leaderboard_data"] = leaderboard_data
        context["yesterday"] = yesterday
        context["tomorrow"] = tomorrow
        return context
