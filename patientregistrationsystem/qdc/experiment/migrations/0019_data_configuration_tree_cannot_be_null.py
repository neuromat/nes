# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0018_initial_data_configuration_tree'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalquestionnaireresponse',
            name='component_configuration',
        ),
        migrations.RemoveField(
            model_name='questionnaireresponse',
            name='component_configuration',
        ),
        migrations.AlterField(
            model_name='eegdata',
            name='data_configuration_tree',
            field=models.ForeignKey(to='experiment.DataConfigurationTree'),
        ),
        migrations.AlterField(
            model_name='questionnaireresponse',
            name='data_configuration_tree',
            field=models.ForeignKey(to='experiment.DataConfigurationTree'),
        ),
    ]
