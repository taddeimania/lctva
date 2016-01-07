from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from app.views.admin import AdminPeekListView, AdminPeekDetailView
from app.views.api import GraphView
from app.views.auth import AuthorizeAPIView, AuthorizePostBackAPIView, RelinkAPIView
from app.views.history import HistoryListView, HistoryDetailView, HistoryFollowersView
from app.views.live import LiveView
from app.views.public import IndexView, AboutView
from app.views.account import SetTimezoneView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index_view"),
    url(r'^about/$', AboutView.as_view(), name="about_view"),
    url(r'^live/$', login_required(LiveView.as_view()), name="live_view"),
    url(r'^history/$', login_required(HistoryListView.as_view()), name="history_list_view"),
    url(r'^history/followers/$', login_required(HistoryFollowersView.as_view()), name="history_followers_view"),
    url(r'^history/(?P<datestamp>\d{4}-\d{2}-\d{2})/$', login_required(HistoryDetailView.as_view()), name="history_detail_view"),
    url(r'^timezone/$', login_required(SetTimezoneView.as_view()), name="timezone_view"),
    url(r'^authorize-api/$', login_required(AuthorizeAPIView.as_view()), name="authorize_api_view"),
    url(r'^relink-api/$', login_required(RelinkAPIView.as_view()), name="relink_api_view"),
    url(r'^authorize-api/postback/', AuthorizePostBackAPIView.as_view(), name="authorize_api_postback_view"),
    url(r'^api/graph/$', GraphView.as_view(), name="graph_view"),
    url(r'^a/(?P<user_slug>[a-z0-9-]+)/$', login_required(AdminPeekListView.as_view()), name="admin_peek_list_view"),
    url(r'^a/(?P<user_slug>[a-z0-9-]+)/(?P<datestamp>\d{4}-\d{2}-\d{2})/$', login_required(AdminPeekDetailView.as_view()), name="admin_peek_detail_view"),
]
