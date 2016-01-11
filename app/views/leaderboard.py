import datetime

from django.views.generic import TemplateView

from app.models import DailyLeaderboard


def get_daily_leaderboard_data(date):
    leaderboard = DailyLeaderboard.objects.filter(date=date)
    leaderboard_data = []
    if leaderboard:
        leaderboard_data = leaderboard.first()
    return leaderboard_data, date + datetime.timedelta(days=-1), date + datetime.timedelta(days=1)


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        data = DailyLeaderboard.objects.first()
        if data:
            date = data.date
            context["leaderboard_data"] = data
            context["yesterday"] = date + datetime.timedelta(days=-1)
            context["tomorrow"] = date + datetime.timedelta(days=1)
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
