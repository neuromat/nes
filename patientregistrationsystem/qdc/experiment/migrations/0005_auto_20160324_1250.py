# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import experiment.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0004_auto_20160318_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_eeg_dir)),
            ],
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('extension', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGData',
            fields=[
                ('datafile_ptr', models.OneToOneField(to='experiment.DataFile', parent_link=True, auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField(default=datetime.date.today, validators=[experiment.models.validate_date_questionnaire_response])),
                ('component_configuration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiment.ComponentConfiguration')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            bases=('experiment.datafile',),
        ),
        migrations.AddField(
            model_name='datafile',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
        ),
    ]
