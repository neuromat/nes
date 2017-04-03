# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0093_text_file_format'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicaldigitalgamephasedata',
            options={'get_latest_by': 'history_date', 'verbose_name': 'historical digital game phase data',
                     'ordering': ('-history_date', '-history_id')},
        ),
        migrations.AddField(
            model_name='experiment',
            name='ethics_committee_project_file',
            field=models.FileField(null=True, verbose_name='Project file approved by the ethics committee',
                                   blank=True, upload_to=experiment.models.get_experiment_dir),
        ),
        migrations.AddField(
            model_name='experiment',
            name='ethics_committee_project_url',
            field=models.URLField(null=True, verbose_name='URL of the project approved by the ethics committee',
                                  blank=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='source_code_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='ethics_committee_project_file',
            field=models.TextField(null=True, verbose_name='Project file approved by the ethics committee',
                                   blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='ethics_committee_project_url',
            field=models.URLField(null=True, verbose_name='URL of the project approved by the ethics committee',
                                  blank=True),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='source_code_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
