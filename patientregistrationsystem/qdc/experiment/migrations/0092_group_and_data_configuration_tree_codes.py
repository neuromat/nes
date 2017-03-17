# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0091_initial_information_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataconfigurationtree',
            name='code',
            field=models.CharField(null=True, max_length=150, blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='code',
            field=models.CharField(null=True, max_length=150, blank=True),
        ),
    ]
