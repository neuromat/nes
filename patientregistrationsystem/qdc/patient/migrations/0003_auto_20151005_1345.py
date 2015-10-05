# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0002_auto_20151005_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='alcoholfrequency',
            name='name_en',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='alcoholfrequency',
            name='name_pt_br',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='alcoholperiod',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='alcoholperiod',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='amountcigarettes',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='amountcigarettes',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='fleshtone',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='fleshtone',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='maritalstatus',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='maritalstatus',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='religion',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='religion',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='schooling',
            name='name_en',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='schooling',
            name='name_pt_br',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
