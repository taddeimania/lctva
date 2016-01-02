
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView

from app.client import LiveCodingClient, LiveCodingAuthClient
from app.models import ApiKey, ApiAccessToken


class AuthorizeAPIView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if ApiAccessToken.objects.filter(user=self.request.user):
            return reverse("live_view")
        base_redirect_url = "https://www.livecoding.tv/o/authorize/?scope=read&state={}&redirect_uri={}&response_type=code&client_id={}"
        key = ApiKey.objects.get(provider="livecodingtv")
        return base_redirect_url.format(key.state, key.redirect_url, key.client_id)


class RelinkAPIView(AuthorizeAPIView):

    def get_redirect_url(self, *args, **kwargs):
        ApiAccessToken.objects.filter(user=self.request.user).delete()
        return super().get_redirect_url(*args, **kwargs)


class AuthorizePostBackAPIView(View):

    def get(self, request):
        code = request.GET.get("code")
        client = LiveCodingAuthClient(code)
        token = client.get_auth_token(request.user)
        livetvuser = LiveCodingClient.get_user_from_token(token)

        user = self.request.user
        try:
            user.userprofile.livetvusername = livetvuser.username.lower()
            user.userprofile.verified = True
            user.userprofile.save()
        except AttributeError:
            return HttpResponseRedirect("{}?api_error={}".format(reverse("account_verify"), livetvuser.detail))
        return HttpResponseRedirect(reverse("live_view"))
