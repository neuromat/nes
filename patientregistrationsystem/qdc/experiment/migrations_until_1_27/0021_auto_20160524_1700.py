# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0020_eeg_equipment_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegsolution',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eegamplifiersetting',
            name='eeg_setting',
            field=models.OneToOneField(primary_key=True, serialize=False, related_name='eeg_amplifier_setting',
                                       to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='eegelectrodelayoutsetting',
            name='eeg_setting',
            field=models.OneToOneField(primary_key=True, serialize=False, related_name='eeg_electrode_layout_setting',
                                       to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='eegfiltersetting',
            name='eeg_setting',
            field=models.OneToOneField(primary_key=True, serialize=False, related_name='eeg_filter_setting',
                                       to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='eegmachinesetting',
            name='eeg_setting',
            field=models.OneToOneField(primary_key=True, serialize=False, related_name='eeg_machine_setting',
                                       to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='eegsolutionsetting',
            name='eeg_setting',
            field=models.OneToOneField(primary_key=True, serialize=False, related_name='eeg_solution_setting',
                                       to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_type',
            field=models.CharField(null=True, blank=True, max_length=50,
                                   choices=[('eeg_machine', 'EEG Machine'), ('eeg_amplifier', 'EEG Amplifier')]),
        ),
    ]
