# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
        ('experiment', '0006_goalkeeper_game_phase'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentResearcher',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
                ('researcher', models.ForeignKey(to='team.Person')),
            ],
        ),
        migrations.RemoveField(
            model_name='researchprojectcollaboration',
            name='research_project',
        ),
        migrations.RemoveField(
            model_name='researchprojectcollaboration',
            name='team_person',
        ),
        migrations.DeleteModel(
            name='ResearchProjectCollaboration',
        ),
    ]
