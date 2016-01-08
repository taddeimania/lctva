import datetime

from django.views.generic import TemplateView

from app.models import DailyLeaderboard


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        yesterday = datetime.date.today() + datetime.timedelta(days=-1)
        leaderboard = DailyLeaderboard.objects.filter(date=yesterday)
        if leaderboard:
            context["leaderboard_data"] = leaderboard.get()
        context["yesterday"] = yesterday
        return context
