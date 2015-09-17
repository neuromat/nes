# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import experiment.models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0001_initial'),
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identification', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('duration_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], null=True, blank=True)),
                ('duration_unit', models.CharField(choices=[('ms', 'milesegundo(s)'), ('s', 'segundo(s)'), ('min', 'minuto(s)'), ('h', 'hora(s)'), ('d', 'dia(s)'), ('w', 'semana(s)'), ('mon', 'mês (meses)'), ('y', 'ano(s)')], max_length=15, null=True, blank=True)),
                ('component_type', models.CharField(choices=[('block', 'Conjunto de passos'), ('instruction', 'Instrução'), ('pause', 'Pausa'), ('questionnaire', 'Questionário'), ('stimulus', 'Estímulo'), ('task', 'Tarefa para o sujeito'), ('task_experiment', 'Tarefa para o experimentador')], max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ComponentConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('number_of_repetitions', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=1, null=True, blank=True)),
                ('interval_between_repetitions_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], null=True, blank=True)),
                ('interval_between_repetitions_unit', models.CharField(choices=[('ms', 'milesegundo(s)'), ('s', 'segundo(s)'), ('min', 'minuto(s)'), ('h', 'hora(s)'), ('d', 'dia(s)'), ('w', 'semana(s)'), ('mon', 'mês (meses)'), ('y', 'ano(s)')], max_length=15, null=True, blank=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('random_position', models.NullBooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('classification_of_diseases', models.ManyToManyField(to='patient.ClassificationOfDiseases', null=True)),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalExperiment',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical experiment',
            },
        ),
        migrations.CreateModel(
            name='HistoricalQuestionnaireResponse',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('token_id', models.IntegerField()),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('component_configuration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.ComponentConfiguration', db_constraint=False, related_name='+', blank=True)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('questionnaire_responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, db_constraint=False, related_name='+', blank=True)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical questionnaire response',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.IntegerField()),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('component_configuration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiment.ComponentConfiguration')),
                ('questionnaire_responsible', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),),
            },
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('keywords', models.ManyToManyField(to='experiment.Keyword')),
                ('owner', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'permissions': (('view_researchproject', 'Can view research project'), ('change_researchproject_from_others', 'Can change research project created by others')),
            },
        ),
        migrations.CreateModel(
            name='StimulusType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient', models.ForeignKey(to='patient.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectOfGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent_form', models.FileField(upload_to=experiment.models.get_dir, null=True)),
                ('group', models.ForeignKey(to='experiment.Group')),
                ('subject', models.ForeignKey(to='experiment.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
                ('number_of_mandatory_components', models.IntegerField(null=True, blank=True)),
                ('type', models.CharField(choices=[('sequence', 'Sequence component'), ('parallel_block', 'Parallel block component')], max_length=20)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
                ('text', models.TextField()),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Pause',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Stimulus',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
                ('stimulus_type', models.ForeignKey(to='experiment.StimulusType')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TaskForTheExperimenter',
            fields=[
                ('component_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='experiment.Component', parent_link=True)),
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
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='research_project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.ResearchProject', db_constraint=False, related_name='+', blank=True),
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
            field=models.ForeignKey(related_name='configuration', to='experiment.Component'),
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
