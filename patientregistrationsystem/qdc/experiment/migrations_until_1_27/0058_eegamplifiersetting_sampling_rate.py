# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0057_data_collection_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegamplifiersetting',
            name='sampling_rate',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)], blank=True),
        ),
    ]
