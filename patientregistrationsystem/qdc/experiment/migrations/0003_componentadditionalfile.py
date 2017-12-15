# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0002_load_brainvision_file_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentAdditionalFile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_step_file_dir)),
                ('component', models.ForeignKey(related_name='component_additional_files', to='experiment.Component')),
            ],
        ),
    ]
