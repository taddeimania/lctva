import datetime
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from pytz import timezone

from app.utils import adjust_time, prepare_data_for_plot


class NodeBaseManager(models.Manager):

    # TODO: could be majorly optimized
    def get_plottable_eight_minutes(self, user):
        return self.get_plottable_last_hour(user)[-100:]

    def get_plottable_last_hour(self, user):
        tz = UserProfile.objects.get(livetvusername=user).tz
        return [(adjust_time(node[0], tz).strftime("%Y-%m-%d %H:%M:%S"), node[1])
                for node in self.get_last_hour(user).values_list('timestamp', 'current_total')]

    def get_x_time_ago(self, user, time_diff):
        time_ago = datetime.datetime.now(timezone(UserProfile.objects.get(livetvusername=user).tz)) - time_diff
        return self.get_all_user_nodes(user).filter(timestamp__gt=time_ago)

    def get_last_hour(self, user):
        return self.get_x_time_ago(user, datetime.timedelta(hours=1))

    def get_all_user_nodes(self, user):
        return self.filter(livetvusername=user)

    def get_all_plottable_user_nodes(self, user):
        nodes = self.get_all_user_nodes(user).values_list('timestamp', 'current_total')
        return prepare_data_for_plot(nodes, user)


class NodeAbstract(models.Model):
    livetvusername = models.CharField(max_length=40, db_index=True)
    current_total = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = NodeBaseManager()

    class Meta:
        abstract = True
        ordering = ["timestamp"]


class NodeManager(NodeBaseManager):

    def get_plottable_last_hour(self, user):
        tz = UserProfile.objects.get(livetvusername=user).tz
        return [(adjust_time(node[0], tz).strftime("%Y-%m-%d %H:%M:%S"), node[1], node[2])
                for node in self.get_last_hour(user).values_list('timestamp', 'current_total', 'total_site_streamers')]


class Node(NodeAbstract):
    total_site_streamers = models.IntegerField()

    objects = NodeManager()

    @property
    def percent(self):
        return (self.current_total / self.total_site_streamers) * 100


class Friends(NodeAbstract):
    pass


class Viewers(NodeAbstract):
    pass


class ApiKey(models.Model):
    client_id = models.TextField()
    client_secret = models.TextField()
    redirect_url = models.TextField()
    provider = models.CharField(max_length=100, unique=True)
    request_count = models.IntegerField(default=0)

    def __str__(self):
        return self.redirect_url

    def increment(self):
        self.request_count += 1
        self.save()

    @property
    def state(self):
        return str(uuid.uuid1())


class ApiAccessToken(models.Model):
    user = models.OneToOneField(User, related_name="token")
    access_code = models.TextField()
    access_token = models.TextField()
    refresh_token = models.TextField()

    @property
    def state(self):
        return str(uuid.uuid1())

    def __str__(self):
        return "{}'s API Token".format(self.user)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    livetvusername = models.CharField(max_length=40, blank=True)
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    frontpaged = models.BooleanField(default=False)
    tz = models.CharField(max_length=100, blank=True, default="America/New_York")

    @property
    def is_authorized(self):
        try:
            return bool(self.user.token)
        except ApiAccessToken.DoesNotExist:
            return False


@receiver(post_save, sender=User)
def add_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class NotificationManager(models.Manager):

    def get_unread_notifications(self, user):
        return self.all().exclude(readers=user)


class Notification(models.Model):
    readers = models.ManyToManyField(User)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()
