
from django.views.generic import TemplateView

from app.models import UserProfile


class IndexView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["is_joel_live"] = UserProfile.objects.get(livetvusername="taddeimania").active
        return context
