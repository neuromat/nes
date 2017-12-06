# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0082_researchprojectcollaboration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='time_between_mep_trials_high',
        ),
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='time_between_mep_trials_low',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='time_between_mep_trials_high',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='time_between_mep_trials_low',
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='coil_orientation_angle',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='second_test_pulse_intensity',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='time_between_mep_trials',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='coil_orientation_angle',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='second_test_pulse_intensity',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='time_between_mep_trials',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
