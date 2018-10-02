# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0002_auto_20180702_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='experimentresearcher',
            name='channel_index',
            field=models.IntegerField(null=True),
        ),
    ]
