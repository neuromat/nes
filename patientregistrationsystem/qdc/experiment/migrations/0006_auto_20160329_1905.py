# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0005_auto_20160324_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileformat',
            name='description_en',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='description_pt_br',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
