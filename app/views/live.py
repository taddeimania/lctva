
from django.views.generic import TemplateView

from app.models import Node
from app.utils import daily_aggregator, trending, unzip_data


class LiveView(TemplateView):
    template_name = "live.html"

    def get_context_data(self):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        all_nodes = Node.objects.get_all_user_nodes(livetvusername)
        if all_nodes:
            current_node = all_nodes.last()
            data = Node.objects.get_plottable_eight_minutes(livetvusername)
            if data:
                dataX, dataY, siteY = unzip_data(data)
                max_viewer_count = 0
                trending_pattern = False
                if data:
                    max_viewer_count = max([_[1] for _ in data])
                    trending_pattern = trending(dataY)

                context["trending"] = trending_pattern
                context["current_node"] = current_node
                context["max_viewer_count"] = max_viewer_count
                if not self.request.user.userprofile.active:
                    context["daily_breakdown"] = daily_aggregator(all_nodes)

        return context
