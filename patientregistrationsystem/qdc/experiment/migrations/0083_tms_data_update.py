# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0082_hotspot_update'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='coil_position_angle',
        ),
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='file_format',
        ),
        migrations.RemoveField(
            model_name='historicaltmsdata',
            name='file_format_description',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='coil_position_angle',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='file',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='file_format',
        ),
        migrations.RemoveField(
            model_name='tmsdata',
            name='file_format_description',
        ),
    ]
