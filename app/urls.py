from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from app.views import IndexView, AboutView, DashboardView, GraphView, FriendsGraphView, ExtraView, HistoryDetailView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index_view"),
    url(r'^about/$', AboutView.as_view(), name="about_view"),
    url(r'^dashboard/$', login_required(DashboardView.as_view()), name="dashboard_view"),
    # url(r'^history/$', ),
    url(r'^history/(?P<datestamp>\d{4}-\d{2}-\d{2})/$', login_required(HistoryDetailView.as_view()), name="history_detail_view"),
    url(r'^extra/$', login_required(ExtraView.as_view()), name="extra_view"),
    url(r'^api/graph/$', GraphView.as_view(), name="graph_view"),
    url(r'^api/graph/friends/$', FriendsGraphView.as_view(), name="friends_graph_view"),
]
