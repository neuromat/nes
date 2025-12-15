# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0003_experimentresearcher_channel_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='experiment',
            field=models.ForeignKey(related_name='components', to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='group',
            name='experiment',
            field=models.ForeignKey(related_name='groups', to='experiment.Experiment', on_delete=models.CASCADE),
        ),
    ]
