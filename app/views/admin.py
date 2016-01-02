
import datetime

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from app.models import Node, Friends
from app.utils import daily_aggregator, unzip_data, prepare_data_for_plot


class AdminPeekListView(TemplateView):
    template_name = "history/list.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, user_slug):
        context = super().get_context_data()
        all_nodes = Node.objects.get_all_user_nodes(user_slug)
        context["daily_breakdown"] = daily_aggregator(all_nodes)
        friend_info = Friends.objects.get_all_plottable_user_nodes(user_slug)
        if friend_info:
            dataX, dataY = unzip_data(friend_info)
            context["friendDataX"] = dataX
            context["friendDataY"] = dataY
            context["friendMaxY"] = max(dataY)
        context["admin_viewing"] = True
        context["admin_viewing_user"] = user_slug
        return context


class AdminPeekDetailView(TemplateView):
    template_name = "history/detail.html"

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, user_slug, datestamp):
        context = super().get_context_data()
        day_nodes = Node.objects.filter(livetvusername=user_slug, timestamp__contains=datetime.datetime.strptime(datestamp, "%Y-%m-%d").date())
        x_data, y_data = unzip_data(prepare_data_for_plot(day_nodes.values_list("timestamp", "current_total")))
        context["breakdown"] = daily_aggregator(day_nodes)[0]
        context["y_data"] = y_data
        context["x_data"] = x_data
        context["max_y"] = max(y_data)
        context["admin_viewing"] = True
        context["admin_viewing_user"] = user_slug
        return context
