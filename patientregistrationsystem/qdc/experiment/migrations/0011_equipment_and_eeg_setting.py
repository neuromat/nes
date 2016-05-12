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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('equipment_type', models.CharField(max_length=50, null=True,
                                                    choices=[('eeg_machine', 'EEG Machine'),
                                                             ('amplifier', 'Amplifier')], blank=True)),
                ('identification', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('serial_number', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting_reason_for_change',
            field=models.TextField(default='', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_equipment'),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='set_of_equipment',
            field=models.ManyToManyField(to='experiment.Equipment'),
        ),
        migrations.AddField(
            model_name='eeg',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting', null=True),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting', null=True),
        ),
    ]
