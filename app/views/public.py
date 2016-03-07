import json
import datetime

from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.utils import timezone as django_timezone

from app.models import Node


class IndexView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class UserOnlineView(View):

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        past = django_timezone.now() - datetime.timedelta(seconds=31)
        online = Node.objects.filter(livetvusername=username, timestamp__gt=past).exists()
        return HttpResponse(json.dumps(online), content_type="application/json")
