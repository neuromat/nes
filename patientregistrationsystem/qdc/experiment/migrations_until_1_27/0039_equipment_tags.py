# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0038_models_for_emg_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
    ]
