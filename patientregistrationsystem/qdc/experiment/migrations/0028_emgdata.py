# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0027_additionaldata'),
    ]

    operations = [
        migrations.CreateModel(
            name='EMGData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_eeg_dir)),
                ('file_format_description', models.TextField(null=True, default='', blank=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
