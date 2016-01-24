
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView

from app.client import LiveCodingClient, LiveCodingAuthClient


class AuthorizeAPIView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return LiveCodingClient.get_redirect_url()


class AuthorizePostBackAPIView(View):

    def get(self, request):
        access_code = request.GET.get('code')
        state = request.GET.get('state')
        try:
            token, refresh = LiveCodingAuthClient(access_code).get_auth_token(request.user)
        except KeyError:
            return HttpResponseRedirect(reverse("index_view"))
        livetvuser = LiveCodingClient.get_user_from_token(token)

        try:
            user = User.objects.get(username=livetvuser.username)
            user.set_password(state)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(livetvuser.username, '', state)
            user.userprofile.livetvusername = livetvuser.username.lower()
            user.userprofile.user = user
        finally:
            user.userprofile.oauth_token = token
            user.userprofile.oauth_refresh_token = refresh
            user.userprofile.oauth_access_code = access_code
            user.userprofile.save()

        user = authenticate(username=livetvuser.username, password=state)
        login(request, user)
        return HttpResponseRedirect(reverse("live_view"))
