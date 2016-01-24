import datetime

from django.views.generic import TemplateView
from django.utils import timezone as django_timezone

from app.models import Node
from app.utils import unzip_data


class LiveView(TemplateView):
    template_name = "live.html"

    def get_context_data(self):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        last_node = Node.objects.get_all_user_nodes(livetvusername).last()
        if last_node:
            if last_node.timestamp < django_timezone.now() + datetime.timedelta(minutes=-1):
                return context
            current_node = last_node
            data = Node.objects.get_plottable_eight_minutes(livetvusername)
            if data:
                dataX, dataY, siteY = unzip_data(data)
                max_viewer_count = max([_[1] for _ in data])
                context["current_node"] = current_node
                context["max_viewer_count"] = max_viewer_count
        return context
