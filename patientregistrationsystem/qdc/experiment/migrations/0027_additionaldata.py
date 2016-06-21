# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0026_create_emg_component'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_eeg_dir)),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
