# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0006_translate_data_into_english'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medicalrecorddata',
            options={'permissions': (('view_medicalrecorddata', 'Can view medical record'),
                                     ('export_medicalrecorddata', 'Can export medical record'))},
        ),
        migrations.AlterModelOptions(
            name='patient',
            options={'permissions': (('view_patient', 'Can view patient'),
                                     ('export_patient', 'Can export patient'))},
        ),
        migrations.AlterModelOptions(
            name='questionnaireresponse',
            options={'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),
                                     ('export_questionnaireresponse', 'Can export questionnaire response'))},
        ),
    ]
