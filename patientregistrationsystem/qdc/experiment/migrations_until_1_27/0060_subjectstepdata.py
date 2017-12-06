# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0059_auto_20160902_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectStepData',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('start_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                                default=datetime.date.today, null=True, blank=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                              default=datetime.date.today, null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('data_configuration_tree', models.ForeignKey(blank=True, to='experiment.DataConfigurationTree',
                                                              null=True)),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
        ),
    ]
