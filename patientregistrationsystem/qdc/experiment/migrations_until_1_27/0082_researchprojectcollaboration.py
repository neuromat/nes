# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
        ('experiment', '0081_tms_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchProjectCollaboration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('is_coordinator', models.BooleanField()),
                ('research_project', models.ForeignKey(to='experiment.ResearchProject', related_name='collaborators')),
                ('team_person', models.ForeignKey(to='team.TeamPerson', related_name='collaborators')),
            ],
        ),
    ]
