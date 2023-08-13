# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SensitiveQuestion',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=150)),
                ('question', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('lime_survey_id', models.IntegerField(unique=True)),
                ('is_initial_evaluation', models.BooleanField(default=True)),
            ],
            options={
                'permissions': (
                    ('view_survey', 'Can view survey'),
                ),
            },
        ),
        migrations.AddField(
            model_name='sensitivequestion',
            name='survey',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='sensitive_questions', to='survey.Survey'),
        ),
        migrations.AlterUniqueTogether(
            name='sensitivequestion',
            unique_together=set([('survey', 'code')]),
        ),
    ]
