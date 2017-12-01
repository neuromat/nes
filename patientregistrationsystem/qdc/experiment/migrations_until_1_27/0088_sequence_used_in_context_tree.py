# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0087_experiment_public_acquisition_concluded'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalgamephasedata',
            name='sequence_used_in_context_tree',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaldigitalgamephasedata',
            name='sequence_used_in_context_tree',
            field=models.TextField(blank=True, null=True),
        ),
    ]
