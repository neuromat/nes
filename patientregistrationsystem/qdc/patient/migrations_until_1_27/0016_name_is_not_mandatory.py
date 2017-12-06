# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0015_schooling_of_the_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpatient',
            name='name',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='name',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
    ]
