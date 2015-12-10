
import json
from statistics import mean

from django import forms
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.forms.util import ErrorList

# import pandas as pd

from app.models import Node, UserProfile, Friends


def trending(data):
    if len(data) < 5:
        return False
    half = len(data) // 2 + 1
    return mean(data[half:]) > mean(data[:half])


def unzip_data(data):
    return [node[1] for node in data], [node[0] for node in data]


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self):
        context = super().get_context_data()
        all_nodes = Node.objects.get_all_user_nodes(self.request.user)
        if all_nodes:
            # df = pd.DataFrame([(obj.timestamp, obj.current_total) for obj in all_nodes], columns=["timestamp", "viewers"])
            # df.index = pd.to_datetime(df.pop("timestamp"), format="%Y-%m-%d %H:%M:%S.%f+00:00")
            # df = df.resample('D', how=["mean", "max", "count"]).dropna().loc[:, "viewers"]
            # df["count"] = df["count"] * 5 / 60

            current_node = all_nodes.last()
            data = Node.objects.get_plottable_eight_minutes(self.request.user)
            dataY, dataX = unzip_data(data)
            max_viewer_count = 0
            trending_pattern = False
            if data:
                max_viewer_count = max([_[1] for _ in data])
                trending_pattern = trending(dataY)

            context["trending"] = trending_pattern
            context["current_node"] = current_node
            context["max_viewer_count"] = max_viewer_count

        return context


class ExtraView(TemplateView):
    template_name = "extra.html"


class AccountCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/create.html"

    def get_success_url(self):
        return reverse("index_view")


class AccountActivateView(UpdateView):
    model = UserProfile
    fields = ["livetvusername"]

    def form_valid(self, form):
        verify_result = form.instance.verify(form.cleaned_data.get("livetvusername"))
        if not verify_result:
            form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                "We couldn't find the LCTVA access token in your profile description. Please add it or check the username is correct."
            ])
            return self.form_invalid(form)

        return HttpResponseRedirect(reverse("index_view"))


class StreamActivateView(View):

    def post(self, request):
        request.user.userprofile.active = True
        request.user.userprofile.save()
        return HttpResponseRedirect(reverse("index_view"))


class StreamDeactivateView(View):

    def post(self, request):
        request.user.userprofile.active = False
        request.user.userprofile.save()
        return HttpResponseRedirect(reverse("index_view"))


class GraphView(View):

    def get(self, request):
        dataY, dataX = unzip_data(Node.objects.get_plottable_eight_minutes(request.user))
        last_node = Node.objects.filter(livetvusername=request.user.userprofile.livetvusername).last()
        current_count = 0
        if last_node:
            current_count = last_node.current_total
        context = {"trending": trending(dataY),
                   "dataX": dataX,
                   "dataY": dataY,
                   "current_count": current_count}
        return HttpResponse(json.dumps(context), content_type="application/json")


class FriendsGraphView(View):

    def get(self, request):
        friend_info = Friends.objects.get_all_plottable_user_nodes(request.user)
        dataY, dataX = unzip_data(friend_info)
        context = {"dataX": dataX,
                   "dataY": dataY}
        return HttpResponse(json.dumps(context), content_type="application/json")
