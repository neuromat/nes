# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0078_emganalogfiltersetting_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emgpreamplifierfiltersetting',
            name='band_pass',
        ),
        migrations.RemoveField(
            model_name='emgpreamplifierfiltersetting',
            name='notch',
        ),
        migrations.AddField(
            model_name='emgpreamplifierfiltersetting',
            name='high_band_pass',
            field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AddField(
            model_name='emgpreamplifierfiltersetting',
            name='high_notch',
            field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AddField(
            model_name='emgpreamplifierfiltersetting',
            name='low_band_pass',
            field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AddField(
            model_name='emgpreamplifierfiltersetting',
            name='low_notch',
            field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
        migrations.AddField(
            model_name='emgpreamplifierfiltersetting',
            name='order',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
    ]
