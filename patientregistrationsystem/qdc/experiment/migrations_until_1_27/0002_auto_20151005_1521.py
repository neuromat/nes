# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stimulustype',
            name='name_en',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='stimulustype',
            name='name_pt_br',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
