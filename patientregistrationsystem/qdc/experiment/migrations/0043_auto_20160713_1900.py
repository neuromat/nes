# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0042_initial_data_electrodemodel_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='filtertype',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_type',
            field=models.CharField(blank=True, choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier'),
                                                        ('eeg_solution', 'EEG Solution'), ('filter', 'Filter'),
                                                        ('eeg_electrode_net', 'EEG Electrode Net'),
                                                        ('ad_converter', 'A/D Converter')], null=True, max_length=50),
        ),
    ]
