
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView

from app.client import LiveCodingClient, LiveCodingAuthClient
from app.models import ApiAccessToken


class AuthorizeAPIView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return LiveCodingClient.get_redirect_url()


class AuthorizePostBackAPIView(View):

    def get(self, request):
        access_code = request.GET.get('code')
        try:
            token, refresh = LiveCodingAuthClient(access_code).get_auth_token(request.user)
        except KeyError:
            return HttpResponseRedirect(reverse("index_view"))
        livetvuser = LiveCodingClient.get_user_from_token(token)

        try:
            user = User.objects.get(username=livetvuser.username)
            user.set_password(access_code)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(livetvuser.username, '', access_code)
            user.userprofile.livetvusername = livetvuser.username.lower()
            user.userprofile.user = user
            user.userprofile.oauth_token = token
            user.userprofile.save()

        if user.is_superuser:
            try:
                access_token = ApiAccessToken.objects.get(user=user)
            except ApiAccessToken.DoesNotExist:
                access_token = ApiAccessToken(user=user)
            access_token.access_code = access_code
            access_token.access_token = token
            access_token.refresh_token = refresh
            access_token.save()

        user = authenticate(username=livetvuser.username, password=access_code)
        login(request, user)
        return HttpResponseRedirect(reverse("live_view"))
