# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from app.models import UserProfile, Node


def migrate_nodes_and_profile_livetvusernames(apps, schema_editor):
    for profile in UserProfile.objects.all():
        profile.livetvusername = profile.livetvusername.lower()
        profile.save()

    for node in Node.objects.all():
        node.livetvusername = node.livetvusername.lower()
        node.save()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_apikey_provider'),
    ]

    operations = [
        migrations.RunPython(migrate_nodes_and_profile_livetvusernames)
    ]
