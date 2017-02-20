# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0060_subjectstepdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='tmsdevicesetting',
            name='coil_model',
            field=models.ForeignKey(to='experiment.CoilModel', null=True),
        ),
    ]
