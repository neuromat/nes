# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0014_eeg_setting_not_null'),
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
            field=models.CharField(null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='name_pt_br',
            field=models.CharField(null=True, max_length=50),
        ),
    ]
