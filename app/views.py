
import datetime
import json
import uuid
from base64 import b64encode

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.forms.util import ErrorList

import requests
from requests.auth import HTTPBasicAuth

from app.models import Node, UserProfile, Friends, ApiKey, ApiAccessToken
from app.utils import daily_aggregator, trending, unzip_data, prepare_data_for_plot


class IndexView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["is_joel_live"] = UserProfile.objects.get(livetvusername="taddeimania").active
        return context


class AuthorizeAPIView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if ApiAccessToken.objects.filter(user=self.request.user):
            return reverse("live_view")
        state = uuid.uuid1()
        base_redirect_url = "https://www.livecoding.tv/o/authorize/?scope=read&state={}&redirect_uri={}&response_type=code&client_id={}"
        key = ApiKey.objects.get()  # do a .get() to ensure only 1 record ever in the DB
        return base_redirect_url.format(state, key.redirect_url, key.client_id)


class AuthorizePostBackAPIView(View):

    def get(self, request):
        state = uuid.uuid1()
        key = ApiKey.objects.get()  # do a .get() to ensure only 1 record ever in the DB
        code = request.GET.get("code")
        url = "https://www.livecoding.tv/o/token/"
        basic_auth_header_val = b64encode(str.encode("{}:{}".format(key.client_id, key.client_secret)))
        payload = "code={}&grant_type=authorization_code&redirect_uri={}&client_id={}&client_secret={}".format(
            code,
            key.redirect_url,
            key.client_id,
            key.client_secret
        )
        headers = {
            'authorization': "Basic " + basic_auth_header_val.decode("utf-8"),
            'cache-control': "no-cache",
            'postman-token': str(state),
            'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=payload, headers=headers).json()
        ApiAccessToken.objects.create(
            user=request.user,
            access_code=code,
            access_token=response['access_token'],
            refresh_token=response['refresh_token'])
        return HttpResponseRedirect(reverse("live_view"))


class LiveView(TemplateView):
    template_name = "live.html"

    def get_context_data(self):
        context = super().get_context_data()
        all_nodes = Node.objects.get_all_user_nodes(self.request.user)
        if all_nodes:
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
            if not self.request.user.userprofile.active:
                context["daily_breakdown"] = daily_aggregator(all_nodes)

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


class GraphView(View):

    def get(self, request):
        dataY, dataX = unzip_data(Node.objects.get_plottable_eight_minutes(request.user))
        last_node = Node.objects.filter(livetvusername=request.user.userprofile.livetvusername).last()
        current_count = 0
        if last_node:
            current_count = last_node.current_total
        context = {"trending": trending(dataY),
                   "frontpaged": request.user.userprofile.frontpaged,
                   "maxY": max(dataY),
                   "dataX": dataX,
                   "dataY": dataY,
                   "current_count": current_count}
        return HttpResponse(json.dumps(context), content_type="application/json")


class FriendsGraphView(View):

    def get(self, request):
        friend_info = Friends.objects.get_all_plottable_user_nodes(request.user)
        dataY, dataX = unzip_data(friend_info)
        context = {"dataX": dataX,
                   "dataY": dataY,
                   "maxY": max(dataY)}
        return HttpResponse(json.dumps(context), content_type="application/json")


# TODO: Total viewers graph view


class HistoryListView(TemplateView):
    template_name = "history/list.html"

    def get_context_data(self):
        context = super().get_context_data()
        all_nodes = Node.objects.get_all_user_nodes(self.request.user)
        context["daily_breakdown"] = daily_aggregator(all_nodes)
        return context


class HistoryDetailView(TemplateView):
    template_name = "history/detail.html"

    def get_context_data(self, datestamp):
        context = super().get_context_data()
        livetvusername = self.request.user.userprofile.livetvusername
        day_nodes = Node.objects.filter(livetvusername=livetvusername, timestamp__contains=datetime.datetime.strptime(datestamp, "%Y-%m-%d").date())
        y_data, x_data = unzip_data(prepare_data_for_plot(day_nodes.values_list("timestamp", "current_total")))
        context["breakdown"] = daily_aggregator(day_nodes)[0]
        context["y_data"] = y_data
        context["x_data"] = x_data
        context["max_y"] = max(y_data)
        return context
