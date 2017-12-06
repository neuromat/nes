# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.db.models.deletion
import django.core.validators

from django.db import models, migrations
from django.conf import settings

import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0001_initial'),
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('identification', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('duration_value', models.IntegerField(blank=True,
                                                       validators=[django.core.validators.MinValueValidator(1)],
                                                       null=True)),
                ('duration_unit', models.CharField(blank=True,
                                                   choices=[('ms', 'milesegundo(s)'), ('s', 'segundo(s)'),
                                                            ('min', 'minuto(s)'), ('h', 'hora(s)'), ('d', 'dia(s)'),
                                                            ('w', 'semana(s)'), ('mon', 'mês (meses)'),
                                                            ('y', 'ano(s)')],
                                                   max_length=15,
                                                   null=True)),
                ('component_type', models.CharField(choices=[('block', 'Conjunto de passos'),
                                                             ('instruction', 'Instrução'),
                                                             ('pause', 'Pausa'),
                                                             ('questionnaire', 'Questionário'),
                                                             ('stimulus', 'Estímulo'),
                                                             ('task', 'Tarefa para o sujeito'),
                                                             ('task_experiment', 'Tarefa para o experimentador')],
                                                    max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ComponentConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('number_of_repetitions', models.IntegerField(
                    blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], default=1)),
                ('interval_between_repetitions_value', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(1)], null=True)),
                ('interval_between_repetitions_unit', models.CharField(
                    blank=True, choices=[('ms', 'milesegundo(s)'), ('s', 'segundo(s)'), ('min', 'minuto(s)'),
                                         ('h', 'hora(s)'), ('d', 'dia(s)'), ('w', 'semana(s)'),
                                         ('mon', 'mês (meses)'), ('y', 'ano(s)')],
                    max_length=15, null=True)),
                ('order', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(1)])),
                ('random_position', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('classification_of_diseases', models.ManyToManyField(to='patient.ClassificationOfDiseases',
                                                                      null=True)),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalExperiment',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL,
                                                   null=True, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical experiment',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalQuestionnaireResponse',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('token_id', models.IntegerField()),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('component_configuration', models.ForeignKey(
                    related_name='+',
                    db_constraint=False,
                    null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    blank=True,
                    to='experiment.ComponentConfiguration')),
                ('history_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    related_name='+', to=settings.AUTH_USER_MODEL)),
                ('questionnaire_responsible', models.ForeignKey(
                    related_name='+', db_constraint=False, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical questionnaire response',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('token_id', models.IntegerField()),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('component_configuration', models.ForeignKey(to='experiment.ComponentConfiguration',
                                                              on_delete=django.db.models.deletion.PROTECT)),
                ('questionnaire_responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),),
            },
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('keywords', models.ManyToManyField(to='experiment.Keyword')),
                ('owner', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions':
                    (('view_researchproject', 'Can view research project'),
                     ('change_researchproject_from_others', 'Can change research project created by others')),
            },
        ),
        migrations.CreateModel(
            name='StimulusType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('patient', models.ForeignKey(to='patient.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectOfGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('consent_form', models.FileField(upload_to=experiment.models.get_dir, null=True)),
                ('group', models.ForeignKey(to='experiment.Group')),
                ('subject', models.ForeignKey(to='experiment.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
                ('number_of_mandatory_components', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(choices=[('sequence', 'Sequence component'),
                                                   ('parallel_block', 'Parallel block component')],
                                          max_length=20)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
                ('text', models.TextField()),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Pause',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
                ('survey', models.ForeignKey(to='survey.Survey', on_delete=django.db.models.deletion.PROTECT)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Stimulus',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
                ('stimulus_type', models.ForeignKey(to='experiment.StimulusType')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TaskForTheExperimenter',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component',
                                                       serialize=False, primary_key=True, auto_created=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.AddField(
            model_name='questionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicalquestionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(related_name='+', db_constraint=False, null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING,
                                    blank=True,
                                    to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='research_project',
            field=models.ForeignKey(related_name='+', db_constraint=False, null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING,
                                    blank=True,
                                    to='experiment.ResearchProject'),
        ),
        migrations.AddField(
            model_name='group',
            name='experimental_protocol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiment.Component'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='research_project',
            field=models.ForeignKey(to='experiment.ResearchProject'),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='component',
            field=models.ForeignKey(to='experiment.Component', related_name='configuration'),
        ),
        migrations.AddField(
            model_name='component',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AlterUniqueTogether(
            name='subjectofgroup',
            unique_together=set([('subject', 'group')]),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='parent',
            field=models.ForeignKey(null=True, related_name='children', to='experiment.Block'),
        ),
        migrations.AlterUniqueTogether(
            name='componentconfiguration',
            unique_together=set([('parent', 'order')]),
        ),
    ]
