# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0005_auto_20180306_1742'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalkeeperGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(unique=True, max_length=2, verbose_name='Code')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GoalkeeperPhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phase', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(to='experiment.GoalkeeperGame')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='goalkeeperphase',
            unique_together=set([('game', 'phase')]),
        ),
    ]
