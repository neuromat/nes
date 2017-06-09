# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0097_rename_goalkeepergame_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalexperiment',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='researchproject',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
