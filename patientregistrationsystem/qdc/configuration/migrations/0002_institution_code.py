# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='code',
            field=models.CharField(null=True, blank=True, max_length=150),
        ),
    ]
