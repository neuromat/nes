# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('acronym', models.CharField(max_length=30, unique=True)),
                ('country', models.CharField(max_length=30)),
                ('parent', models.ForeignKey(null=True, blank=True, related_name='children', to='custom_user.Institution')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='login_enabled',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes, a new login should be created.')], default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='institution',
            field=models.ForeignKey(null=True, blank=True, to='custom_user.Institution'),
        ),
    ]
