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
            name='nes_code',
            field=models.CharField(unique=True, null=True, max_length=50),
        ),
    ]
