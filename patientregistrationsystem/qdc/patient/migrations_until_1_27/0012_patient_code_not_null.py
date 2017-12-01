# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0011_patient_code_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='code',
            field=models.CharField(db_index=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='patient',
            name='code',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
