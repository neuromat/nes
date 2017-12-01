# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0096_experiment_auto_now_fields'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='goalkeepergamelog',
            table='"public"."results"',
        ),
    ]
