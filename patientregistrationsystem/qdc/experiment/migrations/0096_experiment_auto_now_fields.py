# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0095_schedule_of_sending'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='last_update',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='historicalexperiment',
            name='last_update',
            field=models.DateTimeField(editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='scheduleofsending',
            name='schedule_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
