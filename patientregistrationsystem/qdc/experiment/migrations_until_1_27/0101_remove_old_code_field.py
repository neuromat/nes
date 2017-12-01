# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0100_copy_code_to_integer_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataconfigurationtree',
            name='code',
        ),
        # migrations.AddField(
        #     model_name='hotspot',
        #     name='hot_spot_map',
        #     field=models.FileField(null=True, upload_to=experiment.models.get_data_file_dir, blank=True),
        # ),
    ]
