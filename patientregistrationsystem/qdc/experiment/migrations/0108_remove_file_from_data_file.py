# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0107_copying_data_file_to_new_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='additionaldata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='digitalgamephasedata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='eegdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='emgdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='genericdatacollectiondata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicaladditionaldata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicaldigitalgamephasedata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicaleegdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicalemgdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicalgenericdatacollectiondata',
            name='file',
        ),
    ]
