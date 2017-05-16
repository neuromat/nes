# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_institution'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='institution',
            field=models.ForeignKey(to='team.Institution', blank=True, null=True),
        ),
    ]
