# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0009_correction_update_export_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpatient',
            name='code',
            field=models.CharField(null=True, max_length=10, db_index=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='code',
            field=models.CharField(null=True, max_length=10, unique=True),
        ),
    ]
