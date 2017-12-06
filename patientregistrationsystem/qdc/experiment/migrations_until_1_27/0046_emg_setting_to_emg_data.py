# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0045_update_equiment_type_amplifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='emg',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', null=True),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', null=True),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='emg_setting_reason_for_change',
            field=models.TextField(blank=True, null=True, default=''),
        ),
    ]
