# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0021_auto_20160524_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='electrode_model',
            field=models.ForeignKey(to='experiment.EEGElectrodeModel', null=True),
        ),
        migrations.AlterField(
            model_name='eegelectrodenetsystem',
            name='eeg_electrode_localization_system',
            field=models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem', related_name='set_of_electrode_net_system'),
        ),
        migrations.AlterField(
            model_name='eegelectrodenetsystem',
            name='eeg_electrode_net',
            field=models.ForeignKey(to='experiment.EEGElectrodeNet', related_name='set_of_electrode_net_system'),
        ),
        migrations.AlterField(
            model_name='eegelectrodepositionsetting',
            name='eeg_electrode_layout_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodeLayoutSetting', related_name='positions_setting'),
        ),
        migrations.AlterField(
            model_name='eegsolution',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_solution'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_type',
            field=models.CharField(blank=True, choices=[('eeg_machine', 'EEG Machine'), ('eeg_amplifier', 'EEG Amplifier'), ('eeg_solution', 'EEG Solution'), ('eeg_filter', 'EEG Filter'), ('eeg_electrode_net', 'EEG Electrode Net')], max_length=50, null=True),
        ),
    ]
