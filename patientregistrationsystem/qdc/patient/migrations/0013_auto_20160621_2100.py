# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0012_patient_code_not_null'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='patient',
            options={'permissions': (('view_patient', 'Can view patient'), ('export_patient', 'Can export patient'),
                                     ('sensitive_data_patient', 'Can view sensitive patient data'))},
        ),
    ]
