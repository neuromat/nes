# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0040_initial_data_equipment_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='electrodemodel',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AlterField(
            model_name='emgelectrodeplacement',
            name='placement_reference',
            field=models.ForeignKey(null=True, related_name='children', to='experiment.EMGElectrodePlacement',
                                    blank=True),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_type',
            field=models.CharField(null=True, max_length=50,
                                   blank=True, choices=[('eeg_machine', 'EEG Machine'),
                                                        ('eeg_amplifier', 'EEG Amplifier'),
                                                        ('eeg_solution', 'EEG Solution'),
                                                        ('eeg_filter', 'EEG Filter'),
                                                        ('eeg_electrode_net', 'EEG Electrode Net'),
                                                        ('ad_converter', 'A/D Converter')]),
        ),
    ]
