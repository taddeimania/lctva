# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='livetvusername',
            field=models.CharField(max_length=40, default='', db_index=True),
            preserve_default=False,
        ),
    ]
