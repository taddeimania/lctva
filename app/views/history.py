
import datetime

from django.views.generic import TemplateView

from app.models import Node, Friends
from app.utils import daily_aggregator, unzip_data, prepare_data_for_plot


class HistoryListView(TemplateView):
    template_name = "history/list.html"

    def get_context_data(self):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        all_nodes = Node.objects.get_all_user_nodes(livetvusername)
        friend_info = Friends.objects.get_all_plottable_user_nodes(livetvusername)
        dataX, dataY = unzip_data(friend_info)
        context["daily_breakdown"] = daily_aggregator(all_nodes)
        context["friendDataX"] = dataX
        context["friendDataY"] = dataY
        context["friendMaxY"] = max(dataY)
        return context


class HistoryDetailView(TemplateView):
    template_name = "history/detail.html"

    def get_context_data(self, datestamp):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        day_nodes = Node.objects.filter(livetvusername=livetvusername, timestamp__contains=datetime.datetime.strptime(datestamp, "%Y-%m-%d").date())
        x_data, y_data = unzip_data(prepare_data_for_plot(day_nodes.values_list("timestamp", "current_total")))
        context["breakdown"] = daily_aggregator(day_nodes)[0]
        context["y_data"] = y_data
        context["x_data"] = x_data
        context["max_y"] = max(y_data)
        return context
