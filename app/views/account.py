
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView
import pytz

from app.models import UserProfile


class AccountCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/create.html"

    def get_success_url(self):
        return reverse("login")


class AccountActivateView(TemplateView):
    model = UserProfile
    template_name = "app/userprofile_form.html"


class SetTimezoneView(View):

    def get(self, request):
        return render(self.request, 'timezone.html', {'timezones': pytz.common_timezones})

    def post(self, request):
        self.request.user.userprofile.tz = self.request.POST['timezone']
        self.request.user.userprofile.save()
        return render(self.request, 'timezone.html', {'timezones': pytz.common_timezones, 'success': True})
