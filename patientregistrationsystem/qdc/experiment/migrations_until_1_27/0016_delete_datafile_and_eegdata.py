# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0015_translate_fileformat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='file_format',
        ),
        migrations.RemoveField(
            model_name='eegdata',
            name='component_configuration',
        ),
        migrations.RemoveField(
            model_name='eegdata',
            name='datafile_ptr',
        ),
        migrations.RemoveField(
            model_name='eegdata',
            name='eeg_setting',
        ),
        migrations.RemoveField(
            model_name='eegdata',
            name='subject_of_group',
        ),
        migrations.AlterModelOptions(
            name='equipment',
            options={'verbose_name_plural': 'Equipment', 'verbose_name': 'Equipment'},
        ),
        migrations.DeleteModel(
            name='DataFile',
        ),
        migrations.DeleteModel(
            name='EEGData',
        ),
    ]
