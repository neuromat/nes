# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0071_EEGFilterSetting_add_band_pass_and_notch_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='high_band_pass',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='high_notch',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='low_band_pass',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='low_notch',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
