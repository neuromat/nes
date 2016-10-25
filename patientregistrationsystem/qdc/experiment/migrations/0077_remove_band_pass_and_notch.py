# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0076_populate_band_pass_and_notch_range'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emganalogfiltersetting',
            name='band_pass',
        ),
        migrations.RemoveField(
            model_name='emganalogfiltersetting',
            name='notch',
        ),
    ]
