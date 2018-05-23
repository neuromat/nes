# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import configuration.models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, null=True, max_length=255)),
                ('email', models.EmailField(blank=True, null=True, max_length=254)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalInstitution',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, null=True, max_length=150)),
                ('url', models.URLField(blank=True, null=True)),
                ('logo', models.FileField(blank=True, null=True, upload_to=configuration.models.get_institution_logo_dir)),
                ('institution', models.ForeignKey(to='team.Institution')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
