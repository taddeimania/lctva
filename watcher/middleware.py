import pytz

from django.utils import timezone

from app.models import UserProfile


class TimezoneMiddleware(object):

    def process_request(self, request):
        try:
            if request.user.id and request.user.userprofile.tz:
                timezone.activate(pytz.timezone(request.user.userprofile.tz))
            else:
                timezone.deactivate()
        except UserProfile.DoesNotExist:
            timezone.deactivate()
