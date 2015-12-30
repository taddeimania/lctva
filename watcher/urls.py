from django.conf.urls import include, url
from django.contrib import admin

from app.views import AccountCreateView, AccountActivateView

urlpatterns = [
    url(r'^', include('app.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/create/', AccountCreateView.as_view(), name="account_create"),
    url(r'^accounts/verify/', AccountActivateView.as_view(), name="account_verify"),
    url(r'^admin/', include(admin.site.urls)),
]
