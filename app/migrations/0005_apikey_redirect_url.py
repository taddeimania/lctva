# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_apiaccesstoken_apikey'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='redirect_url',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
