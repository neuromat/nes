# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import configuration.models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_institution'),
        ('configuration', '0002_institution_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalInstitution',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=150, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('logo', models.FileField(blank=True,
                                          upload_to=configuration.models.get_institution_logo_dir, null=True)),
                ('institution', models.ForeignKey(to='team.Institution')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
