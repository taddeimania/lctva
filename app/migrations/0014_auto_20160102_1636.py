# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_apikey_request_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apikey',
            old_name='request_Count',
            new_name='request_count',
        ),
    ]
