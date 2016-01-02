# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_userprofile_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='request_Count',
            field=models.IntegerField(default=0),
        ),
    ]
