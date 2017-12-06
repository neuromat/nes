# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0102_rename_code_number_to_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotspot',
            name='hot_spot_map',
            field=models.FileField(null=True, upload_to=experiment.models.get_data_file_dir, blank=True),
        ),
    ]
