# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0004_institution_data_migration'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Institution',
        ),
    ]
