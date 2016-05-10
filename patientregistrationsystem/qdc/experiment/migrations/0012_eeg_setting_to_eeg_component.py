# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0011_eeg_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='eeg',
            name='eeg_setting',
            field=models.ForeignKey(null=True, to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_model',
            field=models.ForeignKey(related_name='set_of_equipment', to='experiment.EquipmentModel'),
        ),
        migrations.AlterField(
            model_name='equipmentmodel',
            name='manufacturer',
            field=models.ForeignKey(related_name='equipment_models', to='experiment.Manufacturer'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting',
            field=models.ForeignKey(null=True, to='experiment.EEGSetting'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting_reason_for_change',
            field=models.TextField(null=True, blank=True, default=''),
        ),
    ]
