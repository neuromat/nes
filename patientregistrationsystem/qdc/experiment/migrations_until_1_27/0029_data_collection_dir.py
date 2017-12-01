# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0028_emgdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldata',
            name='file',
            field=models.FileField(upload_to=experiment.models.get_data_file_dir),
        ),
        migrations.AlterField(
            model_name='eegdata',
            name='file',
            field=models.FileField(upload_to=experiment.models.get_data_file_dir),
        ),
        migrations.AlterField(
            model_name='emgdata',
            name='file',
            field=models.FileField(upload_to=experiment.models.get_data_file_dir),
        ),
    ]
