# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0014_update_sensitive_data_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsocialdemographicdata',
            name='patient_schooling',
            field=models.ForeignKey(db_constraint=False, related_name='+', to='patient.Schooling', on_delete=django.db.models.deletion.DO_NOTHING, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='socialdemographicdata',
            name='patient_schooling',
            field=models.ForeignKey(verbose_name='Schooling of the patient', to='patient.Schooling', related_name='patient_schooling_set', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='socialdemographicdata',
            name='schooling',
            field=models.ForeignKey(verbose_name='Schooling of the householder', to='patient.Schooling', null=True, blank=True),
        ),
    ]
