# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0004_auto_20160225_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classificationofdiseases',
            name='abbreviated_description',
            field=models.CharField(max_length=190),
        ),
        migrations.AlterField(
            model_name='classificationofdiseases',
            name='abbreviated_description_en',
            field=models.CharField(null=True, max_length=190),
        ),
        migrations.AlterField(
            model_name='classificationofdiseases',
            name='abbreviated_description_pt_br',
            field=models.CharField(null=True, max_length=190),
        ),
    ]
