# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0007_add_experiment_researcher'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamperson',
            name='person',
        ),
        migrations.RemoveField(
            model_name='teamperson',
            name='team',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
        migrations.DeleteModel(
            name='TeamPerson',
        ),
    ]
