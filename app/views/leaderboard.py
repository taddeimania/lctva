
from django.views.generic import TemplateView


class LeaderBoardDailyView(TemplateView):
    template_name = "leaderboard/today.html"

    def get_context_data(self):
        context = super().get_context_data()
        return context
