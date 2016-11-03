# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0081_tms_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalhotspot',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalhotspot',
            name='tms_data',
        ),
        migrations.RemoveField(
            model_name='historicalhotspot',
            name='tms_position',
        ),
        migrations.AlterField(
            model_name='block',
            name='type',
            field=models.CharField(choices=[('sequence', 'Sequence'), ('parallel_block', 'Parallel')], max_length=20),
        ),
        migrations.DeleteModel(
            name='HistoricalHotSpot',
        ),
    ]
