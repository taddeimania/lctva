import datetime
import uuid

from bs4 import BeautifulSoup
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import requests


def adjust_time(timestamp):
    return timestamp - datetime.timedelta(hours=5)


class NodeManager(models.Manager):

    def get_plottable_eight_minutes(self, user):
        return self.get_plottable_last_hour(user)[-100:]

    def get_plottable_last_hour(self, user):
        return [(adjust_time(node[0]).strftime("%Y-%m-%d %H:%M:%S"), node[1])
                for node in self.get_last_hour(user).values_list('timestamp', 'current_total')]

    def get_x_time_ago(self, user, time_diff):
        time_ago = datetime.datetime.now() - time_diff
        return self.get_all_user_nodes(user).filter(timestamp__gt=time_ago)

    def get_last_hour(self, user):
        return self.get_x_time_ago(user, datetime.timedelta(hours=1))

    def get_all_user_nodes(self, user):
        return self.filter(livetvusername=user.userprofile.livetvusername)

    def get_all_plottable_user_nodes(self, user):
        nodes = self.get_all_user_nodes(user).values_list('timestamp', 'current_total')
        return [(adjust_time(node[0]).strftime("%Y-%m-%d %H:%M:%S"), node[1])
                for node in nodes]


class NodeAbstract(models.Model):
    livetvusername = models.CharField(max_length=40, db_index=True)
    current_total = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = NodeManager()

    class Meta:
        abstract = True
        ordering = ["timestamp"]

    @property
    def time(self):
        return adjust_time(self.timestamp).strftime("%d/%m/%y %H:%M:%S")

    def __str__(self):
        return "{} - {}".format(self.time, self.current_total)


class Node(NodeAbstract):
    pass


class Friends(NodeAbstract):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    livetvusername = models.CharField(max_length=40, blank=True)
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    @property
    def is_user_currently_streaming(self):
        body = requests.get("https://www.livecoding.tv/livestreams/").content
        souper = BeautifulSoup(body, "html.parser")
        is_streaming = souper.find("a", {
            "class": "browse-main-videos--thumbnail",
            "href": "/{}/".format(self.livetvusername)})
        return bool(is_streaming)

    def activate(self, username):
        body = requests.get("https://livecoding.tv/{}/".format(username)).content
        bs = BeautifulSoup(body, "html.parser")
        if "lctva={}".format(self.token) in bs.find("div", {"class": "stream-desc-info--desc"}).text:
            self.active = True
            self.save()
        else:
            raise Exception("woops")

    def verify(self, username):
        body = requests.get("https://livecoding.tv/{}/".format(username)).content
        bs = BeautifulSoup(body, "html.parser")
        result = bs.find("div", {"class": "stream-desc-info--desc"})
        if result:
            if "lctva={}".format(self.token) in result.text:
                self.verified = True
                self.save()
                return True
        else:
            self.verified = False
            self.save()
            return False


@receiver(post_save, sender=User)
def add_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
