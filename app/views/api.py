
import json

from django.http import HttpResponse
from django.views.generic import View

from app.models import Node, Notification
from app.utils import unzip_data


class ViewerGraphView(View):

    def get(self, request):
        dataX, dataY = unzip_data(Node.objects.get_eight_minutes_of_total_viewers())
        context = {
            "dataX": dataX,
            "dataY": dataY,
            "maxY": max(dataY)
        }
        return HttpResponse(json.dumps(context), content_type="application/json")


class GraphView(View):

    def get(self, request):
        livetvusername = request.user.userprofile.livetvusername
        dataX, dataY, siteY = unzip_data(Node.objects.get_plottable_eight_minutes(livetvusername))
        last_node = Node.objects.filter(livetvusername=livetvusername).last()
        current_count = 0
        if last_node:
            current_count = last_node.current_total
        context = {"frontpaged": request.user.userprofile.frontpaged,
                   "maxY": max(dataY),
                   "maxSiteY": max(siteY),
                   "dataX": dataX,
                   "dataY": dataY,
                   "siteY": siteY,
                   "current_count": current_count}
        return HttpResponse(json.dumps(context), content_type="application/json")


class NotificationCountAPIView(View):

    def get(self, request):
        count = Notification.objects.get_unread_notifications(request.user).count()
        return HttpResponse(json.dumps(count), content_type="application/json")
