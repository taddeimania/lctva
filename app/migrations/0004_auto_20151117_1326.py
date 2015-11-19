# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_node_livetvusername'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False, auto_created=True, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='token',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
