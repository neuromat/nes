# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0004_scheduleofsending_send_participant_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleofsending',
            name='send_participant_age',
            field=models.BooleanField(),
        ),
    ]
