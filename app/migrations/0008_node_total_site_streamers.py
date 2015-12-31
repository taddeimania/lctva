# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_userprofile_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='total_site_streamers',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
