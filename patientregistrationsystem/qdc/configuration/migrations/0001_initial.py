# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import configuration.models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RightsSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
                'permissions': (('upgrade_rights', 'Can upgrade NES version'),),
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalInstitution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=150, null=True, blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('logo', models.FileField(upload_to=configuration.models.get_institution_logo_dir, null=True,
                                          blank=True)),
                ('institution', models.ForeignKey(on_delete=models.CASCADE, to='custom_user.Institution', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
