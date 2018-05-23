# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RightsSupport',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
            ],
            options={
                'managed': False,
                'permissions': (('upgrade_rights', 'Can upgrade NES version'),),
            },
        ),
    ]
