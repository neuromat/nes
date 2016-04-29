# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0008_initial_data_file_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='file_format_description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
