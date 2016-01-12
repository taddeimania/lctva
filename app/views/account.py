
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from django.views.generic.list import ListView
import pytz

from app.models import Notification


class SetTimezoneView(View):

    def get(self, request):
        return render(self.request, 'timezone.html', {'timezones': pytz.common_timezones})

    def post(self, request):
        self.request.user.userprofile.tz = self.request.POST['timezone']
        self.request.user.userprofile.save()
        return render(self.request, 'timezone.html', {'timezones': pytz.common_timezones, 'success': True})


class NotificationListView(ListView):
    model = Notification

    def get_queryset(self):
        qs = Notification.objects.all()
        for notification in qs.exclude(readers=self.request.user):
            notification.readers.add(self.request.user)
        return qs

    def get_context_data(self):
        context = super().get_context_data()
        context["current_time"] = timezone.now()
        return context
