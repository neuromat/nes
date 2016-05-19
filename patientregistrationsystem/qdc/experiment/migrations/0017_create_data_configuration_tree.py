# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0016_delete_datafile_and_eegdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataConfigurationTree',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('component_configuration', models.ForeignKey(to='experiment.ComponentConfiguration', on_delete=django.db.models.deletion.PROTECT)),
                ('parent', models.ForeignKey(to='experiment.DataConfigurationTree', null=True, related_name='children')),
            ],
        ),
        migrations.CreateModel(
            name='EEGData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[experiment.models.validate_date_questionnaire_response])),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_eeg_dir)),
                ('file_format_description', models.TextField(blank=True, null=True, default='')),
                ('eeg_setting_reason_for_change', models.TextField(blank=True, null=True, default='')),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', null=True)),
                ('eeg_setting', models.ForeignKey(to='experiment.EEGSetting')),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='historicalquestionnaireresponse',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, to='experiment.DataConfigurationTree', null=True, related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False),
        ),
        migrations.AddField(
            model_name='questionnaireresponse',
            name='data_configuration_tree',
            field=models.ForeignKey(to='experiment.DataConfigurationTree', null=True),
        ),
    ]
