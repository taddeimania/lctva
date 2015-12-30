from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from app.views import IndexView, AboutView, LiveView, GraphView, FriendsGraphView, HistoryListView, HistoryDetailView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index_view"),
    url(r'^about/$', AboutView.as_view(), name="about_view"),
    url(r'^live/$', login_required(LiveView.as_view()), name="live_view"),
    url(r'^history/$', login_required(HistoryListView.as_view()), name="history_list_view"),
    url(r'^history/(?P<datestamp>\d{4}-\d{2}-\d{2})/$', login_required(HistoryDetailView.as_view()), name="history_detail_view"),
    url(r'^api/graph/$', GraphView.as_view(), name="graph_view"),
    url(r'^api/graph/friends/$', FriendsGraphView.as_view(), name="friends_graph_view"),
]
