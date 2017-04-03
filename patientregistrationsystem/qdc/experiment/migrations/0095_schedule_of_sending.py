# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiment', '0094_experiment_fields_source_code_url_and_ethics_committee_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleOfSending',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('schedule_datetime', models.DateTimeField(default=datetime.datetime(2017, 3, 30, 14, 4, 25, 122376))),
                ('status', models.CharField(choices=[('scheduled', 'scheduled'), ('canceled', 'canceled'), ('sending', 'sending'), ('sent', 'sent'), ('error_sending', 'error sending')], max_length=50)),
                ('sending_datetime', models.DateTimeField(null=True)),
                ('reason_for_resending', models.CharField(null=True, max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='experiment',
            name='last_sending',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 30, 14, 4, 24, 954346)),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='last_sending',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 30, 14, 4, 24, 954346)),
        ),
        migrations.AddField(
            model_name='scheduleofsending',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', related_name='schedule_of_sending'),
        ),
        migrations.AddField(
            model_name='scheduleofsending',
            name='responsible',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
