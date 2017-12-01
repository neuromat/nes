# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0006_fileformat_nes_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='file_format_description',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='fileformat',
            name='nes_code',
            field=models.CharField(null=True, max_length=50, blank=True, unique=True),
        ),
    ]
