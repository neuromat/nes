# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0003_componentadditionalfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleofsending',
            name='send_participant_age',
            field=models.BooleanField(default=True),
        ),
    ]
