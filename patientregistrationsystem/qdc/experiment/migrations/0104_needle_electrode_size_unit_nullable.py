# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0103_hotspot_hot_spot_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='needleelectrode',
            name='size_unit',
            field=models.CharField(choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], blank=True, max_length=10, null=True),
        ),
    ]
