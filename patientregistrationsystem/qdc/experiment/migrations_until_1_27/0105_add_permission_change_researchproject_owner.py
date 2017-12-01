# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0104_needle_electrode_size_unit_nullable'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='researchproject',
            options={'permissions': (('view_researchproject', 'Can view research project'), ('change_researchproject_from_others', 'Can change research project created by others'), ('change_researchproject_owner', 'Can change research project owner'))},
        ),
    ]
