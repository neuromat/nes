# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0077_remove_band_pass_and_notch'),
    ]

    operations = [
        migrations.AddField(
            model_name='emganalogfiltersetting',
            name='order',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True),
        ),
    ]
