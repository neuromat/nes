# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import datetime
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiment', '0085_component_type_field_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalGamePhaseData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('file_format_description', models.TextField(null=True, default='', blank=True)),
                ('data_configuration_tree', models.ForeignKey(null=True, blank=True,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalDigitalGamePhaseData',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', blank=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(null=True, default='', blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(null=True,
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              db_constraint=False, related_name='+',
                                                              blank=True, to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                  db_constraint=False, related_name='+', blank=True,
                                                  to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                   related_name='+', to=settings.AUTH_USER_MODEL)),
                ('subject_of_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                       db_constraint=False, related_name='+', blank=True,
                                                       to='experiment.SubjectOfGroup')),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical digital game phase data',
            },
        ),
        migrations.AlterField(
            model_name='contexttree',
            name='setting_file',
            field=models.FileField(null=True, blank=True, upload_to=experiment.models.get_context_tree_dir),
        ),
    ]
