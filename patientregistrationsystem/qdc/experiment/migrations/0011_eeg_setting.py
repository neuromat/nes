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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('identification', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('serial_number', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('equipment_type', models.CharField(choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentModel',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('identification', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Amplifier',
            fields=[
                ('equipmentcategory_ptr', models.OneToOneField(to='experiment.EquipmentCategory', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
            ],
            bases=('experiment.equipmentcategory',),
        ),
        migrations.CreateModel(
            name='EEGMachine',
            fields=[
                ('equipmentcategory_ptr', models.OneToOneField(to='experiment.EquipmentCategory', auto_created=True, serialize=False, parent_link=True, primary_key=True)),
            ],
            bases=('experiment.equipmentcategory',),
        ),
        migrations.AddField(
            model_name='equipmentmodel',
            name='equipment_category',
            field=models.ForeignKey(to='experiment.EquipmentCategory'),
        ),
        migrations.AddField(
            model_name='equipmentmodel',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='equipment_model',
            field=models.ForeignKey(to='experiment.EquipmentModel'),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='set_of_equipment',
            field=models.ManyToManyField(to='experiment.Equipment'),
        ),
    ]
