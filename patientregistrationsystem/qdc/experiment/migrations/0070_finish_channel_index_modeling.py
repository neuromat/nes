# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0069_populate_channel_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eegelectrodeposition',
            name='channel_default_index',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='eegelectrodepositioncollectionstatus',
            name='channel_index',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='eegelectrodepositionsetting',
            name='channel_index',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodeposition',
            unique_together=set([('eeg_electrode_localization_system', 'channel_default_index')]),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodepositioncollectionstatus',
            unique_together=set([('eeg_data', 'channel_index')]),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodepositionsetting',
            unique_together=set([('eeg_electrode_layout_setting', 'channel_index')]),
        ),
    ]
