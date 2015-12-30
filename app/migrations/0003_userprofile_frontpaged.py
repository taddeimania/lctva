# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_viewers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='frontpaged',
            field=models.BooleanField(default=False),
        ),
    ]
