# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('acronym', models.CharField(unique=True, max_length=30)),
                ('country', models.CharField(max_length=30)),
                ('parent', models.ForeignKey(null=True, to='team.Institution', related_name='children')),
            ],
        ),
    ]
