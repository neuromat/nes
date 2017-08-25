# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0003_person_institution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='parent',
            field=models.ForeignKey(null=True, to='team.Institution', related_name='children', blank=True),
        ),
    ]
