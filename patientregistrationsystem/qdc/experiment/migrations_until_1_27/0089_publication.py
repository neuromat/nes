# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0088_sequence_used_in_context_tree'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('citation', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('experiments', models.ManyToManyField(to='experiment.Experiment')),
            ],
        ),
    ]
