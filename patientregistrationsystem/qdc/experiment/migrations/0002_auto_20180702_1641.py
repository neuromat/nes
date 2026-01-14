# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experimentresearcher',
            name='experiment',
            field=models.ForeignKey(related_name='researchers', to='experiment.Experiment', on_delete=models.CASCADE),
        ),
    ]
