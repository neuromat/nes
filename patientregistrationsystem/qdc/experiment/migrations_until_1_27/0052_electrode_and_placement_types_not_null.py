# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0051_default_to_electrode_and_placement_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electrodemodel',
            name='electrode_type',
            field=models.CharField(max_length=50, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'),
                                                           ('needle', 'Needle')]),
        ),
        migrations.AlterField(
            model_name='emgelectrodeplacement',
            name='placement_type',
            field=models.CharField(max_length=50, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'),
                                                           ('needle', 'Needle')]),
        ),
    ]
