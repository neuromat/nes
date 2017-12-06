# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0003_auto_20151005_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificationofdiseases',
            name='abbreviated_description_en',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='classificationofdiseases',
            name='abbreviated_description_pt_br',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='classificationofdiseases',
            name='description_en',
            field=models.CharField(null=True, max_length=300),
        ),
        migrations.AddField(
            model_name='classificationofdiseases',
            name='description_pt_br',
            field=models.CharField(null=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='address_number',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicaltelephone',
            name='type',
            field=models.CharField(max_length=15, choices=[('MO', 'Cell phone'), ('HO', 'Home phone'),
                                                           ('WO', 'Business'), ('MA', 'Main'),
                                                           ('FW', 'Business fax'), ('FH', 'Home fax'),
                                                           ('PA', 'Pager'), ('OT', 'Other')],
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='address_number',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='telephone',
            name='type',
            field=models.CharField(max_length=15, choices=[('MO', 'Cell phone'), ('HO', 'Home phone'),
                                                           ('WO', 'Business'), ('MA', 'Main'),
                                                           ('FW', 'Business fax'), ('FH', 'Home fax'),
                                                           ('PA', 'Pager'), ('OT', 'Other')],
                                   blank=True),
        ),
    ]
