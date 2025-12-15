# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('acronym', models.CharField(unique=True, max_length=30)),
                ('country', models.CharField(max_length=30)),
                ('parent', models.ForeignKey(blank=True, related_name='children', null=True,
                                             to='custom_user.Institution', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('login_enabled', models.BooleanField(
                    choices=[(False, 'No'), (True, 'Yes, a username and password must be configured')], default=False)
                 ),
                ('force_password_change', models.BooleanField(default=True)),
                ('institution', models.ForeignKey(blank=True, null=True, to='custom_user.Institution', on_delete=models.CASCADE)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
