
import datetime

from django.views.generic import TemplateView

from app.client import LiveCodingClient
from app.models import Node, Friends
from app.utils import daily_aggregator, unzip_data, prepare_data_for_plot


class HistoryListView(TemplateView):
    template_name = "history/list.html"

    def get_context_data(self):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        all_nodes = Node.objects.get_all_user_nodes(livetvusername)
        friend_info = Friends.objects.get_all_plottable_user_nodes(livetvusername)
        context["daily_breakdown"] = daily_aggregator(all_nodes)
        if friend_info:
            dataX, dataY = unzip_data(friend_info)
            context["friendDataX"] = dataX
            context["friendDataY"] = dataY
            context["friendMaxY"] = max(dataY)
        return context


class HistoryDetailView(TemplateView):
    template_name = "history/detail.html"

    def get_context_data(self, datestamp):
        context = super().get_context_data()
        day = datetime.datetime.strptime(datestamp, "%Y-%m-%d").date()
        livetvusername = self.request.user.userprofile.livetvusername
        day_nodes = Node.objects.filter(livetvusername=livetvusername, timestamp__contains=day)
        x_data, y_data = unzip_data(prepare_data_for_plot(day_nodes.values_list("timestamp", "current_total"), livetvusername))
        context["breakdown"] = daily_aggregator(day_nodes)[0]
        context["y_data"] = y_data
        context["x_data"] = x_data
        context["videos"] = [vid for generator in LiveCodingClient(livetvusername).get_user_videos() for vid in generator if datetime.datetime.strptime(vid.creation_time, "%Y-%m-%dT%H:%M:%S.%fZ").date() == day]
        context["max_y"] = max(y_data)
        return context


class HistoryFollowersView(TemplateView):
    template_name = "history/followers.html"

    def get_context_data(self):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        friend_info = Friends.objects.get_all_plottable_user_nodes(livetvusername)
        if friend_info:
            dataX, dataY = unzip_data(friend_info)
            context["friendDataX"] = dataX
            context["friendDataY"] = dataY
            context["friendMaxY"] = max(dataY)
        return context
