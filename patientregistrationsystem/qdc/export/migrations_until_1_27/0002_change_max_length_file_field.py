# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import export.models


class Migration(migrations.Migration):

    dependencies = [
        ('export', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='input_file',
            field=models.FileField(upload_to=export.models.get_export_dir, max_length=1000),
        ),
        migrations.AlterField(
            model_name='export',
            name='output_export',
            field=models.FileField(upload_to=export.models.get_export_dir, max_length=1000),
        ),
    ]
