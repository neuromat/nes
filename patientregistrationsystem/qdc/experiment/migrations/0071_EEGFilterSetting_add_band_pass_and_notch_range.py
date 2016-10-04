# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0070_finish_channel_index_modeling'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegfiltersetting',
            name='high_band_pass',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)], blank=True),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='high_notch',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)], blank=True),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='low_band_pass',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)], blank=True),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='low_notch',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)], blank=True),
        ),
    ]
