# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0029_data_collection_dir'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='equipment',
            options={'verbose_name': 'Equipment', 'permissions': (('register_equipment', 'Can register equipment'),),
                     'verbose_name_plural': 'Equipment'},
        ),
    ]
