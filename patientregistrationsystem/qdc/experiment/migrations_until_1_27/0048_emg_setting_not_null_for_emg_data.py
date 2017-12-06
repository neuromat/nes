# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0047_create_emg_setting_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emg',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting'),
        ),
        migrations.AlterField(
            model_name='emgdata',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting'),
        ),
    ]
