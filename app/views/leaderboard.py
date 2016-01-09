import datetime

from django.views.generic import TemplateView
from django.utils import timezone

from app.models import DailyLeaderboard


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        yesterday = timezone.now().date() + datetime.timedelta(days=-1)
        leaderboard = DailyLeaderboard.objects.filter(date=yesterday)
        if leaderboard:
            context["leaderboard_data"] = leaderboard.first()
        context["yesterday"] = yesterday
        return context
