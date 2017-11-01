# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_sensitive_question'),
        ('experiment', '0109_auto_20171005_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalSelectedQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('question_code', models.CharField(max_length=150)),
                ('experiment', models.ForeignKey(to='experiment.Experiment', related_name='portal_selected_questions')),
                ('survey', models.ForeignKey(to='survey.Survey')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='portalselectedquestion',
            unique_together=set([('experiment', 'survey', 'question_code')]),
        ),
    ]
