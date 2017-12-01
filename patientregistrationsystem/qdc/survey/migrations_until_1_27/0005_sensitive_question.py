# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_questionnaire_code_not_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='SensitiveQuestion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=150)),
                ('question', models.TextField()),
                ('survey', models.ForeignKey(related_name='sensitive_questions', to='survey.Survey')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='sensitivequestion',
            unique_together=set([('survey', 'code')]),
        ),
    ]
