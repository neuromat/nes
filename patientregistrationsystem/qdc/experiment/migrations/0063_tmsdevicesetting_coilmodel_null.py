# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0062_populate_tmsdevicesetting_coil_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tmsdevice',
            name='coil_model',
        ),
        migrations.AlterField(
            model_name='tmsdevicesetting',
            name='coil_model',
            field=models.ForeignKey(to='experiment.CoilModel'),
        ),
    ]
