
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.base import RedirectView

from app.client import LiveCodingClient, LiveCodingAuthClient
from app.models import ApiAccessToken


class AuthorizeAPIView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if ApiAccessToken.objects.filter(user=self.request.user):
            return reverse("live_view")
        return LiveCodingClient.get_redirect_url()


class RelinkAPIView(AuthorizeAPIView):

    def get_redirect_url(self, *args, **kwargs):
        ApiAccessToken.objects.filter(user=self.request.user).delete()
        return super().get_redirect_url(*args, **kwargs)


class AuthorizePostBackAPIView(View):

    def get(self, request):
        token = LiveCodingAuthClient(request.GET.get('code')).get_auth_token(request.user)
        livetvuser = LiveCodingClient.get_user_from_token(token)

        if not request.user.id:
            # No logged in user, either find a userprofile in the DB that matches the livetvuser
            # and log them in, or make a new user/profile and set the livetvuser to the profile attr
            pass
        else:
            user = request.user
            try:
                user.userprofile.livetvusername = livetvuser.username.lower()
                user.userprofile.verified = True
                user.userprofile.save()
            except AttributeError:
                return HttpResponseRedirect("{}?api_error={}".format(reverse("account_verify"), livetvuser.detail))
        return HttpResponseRedirect(reverse("live_view"))
