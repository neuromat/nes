# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_questionnaire_code_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='code',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
