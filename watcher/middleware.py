import pytz

from django.utils import timezone


class TimezoneMiddleware(object):

    def process_request(self, request):
        if request.user.id and request.user.userprofile.tz:
            timezone.activate(pytz.timezone(request.user.userprofile.tz))
        else:
            timezone.deactivate()
