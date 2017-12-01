# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0033_tag'),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EEGElectrodeModel",
            new_name="ElectrodeModel"
        ),

        migrations.RenameModel(
            old_name="EEGAmplifier",
            new_name="Amplifier"
        ),

        migrations.RenameModel(
            old_name="EEGFilterType",
            new_name="FilterType"
        ),
    ]
