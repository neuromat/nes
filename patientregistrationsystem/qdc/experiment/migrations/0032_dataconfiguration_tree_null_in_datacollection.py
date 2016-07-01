# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0031_update_equipment_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree'),
        ),
        migrations.AlterField(
            model_name='eegdata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree'),
        ),
        migrations.AlterField(
            model_name='emgdata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree'),
        ),
        migrations.AlterField(
            model_name='questionnaireresponse',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree'),
        ),
    ]
