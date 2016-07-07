# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0034_refactoring_eeg_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileformat',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
    ]
