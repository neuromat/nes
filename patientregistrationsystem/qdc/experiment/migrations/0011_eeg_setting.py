# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0010_auto_20160428_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='EEGSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('equipment_type', models.CharField(max_length=30, choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier')])),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Amplifier',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True, to='experiment.Equipment', serialize=False)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGMachine',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True, to='experiment.Equipment', serialize=False)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer'),
        ),
    ]
