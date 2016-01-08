import datetime

from django.views.generic import TemplateView

from app.models import Leaderboard


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        leaderboard = Leaderboard.objects.filter(date=datetime.date.today() + datetime.timedelta(days=-1))
        if leaderboard:
            context["leaderboard_data"] = leaderboard.get()
        return context
