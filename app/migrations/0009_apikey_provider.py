# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_node_total_site_streamers'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='provider',
            field=models.CharField(unique=True, max_length=100, default=''),
            preserve_default=False,
        ),
    ]
