# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0101_remove_old_code_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataconfigurationtree',
            old_name='code_number',
            new_name='code',
        ),
        # migrations.AddField(
        #     model_name='hotspot',
        #     name='hot_spot_map',
        #     field=models.FileField(upload_to=experiment.models.get_data_file_dir, blank=True, null=True),
        # ),
    ]
