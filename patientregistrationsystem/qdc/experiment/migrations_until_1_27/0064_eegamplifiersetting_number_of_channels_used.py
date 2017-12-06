# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0063_tmsdevicesetting_coilmodel_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegamplifiersetting',
            name='number_of_channels_used',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
    ]
