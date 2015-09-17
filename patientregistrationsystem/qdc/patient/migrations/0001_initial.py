# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import patient.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlcoholFrequency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AlcoholPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AmountCigarettes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationOfDiseases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=300)),
                ('abbreviated_description', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(null=True, related_name='children', to='patient.ClassificationOfDiseases')),
            ],
        ),
        migrations.CreateModel(
            name='ComplementaryExam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=500)),
                ('doctor', models.CharField(max_length=50, null=True, blank=True)),
                ('doctor_register', models.CharField(max_length=10, null=True, blank=True)),
                ('exam_site', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Diagnosis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True)),
                ('description', models.CharField(max_length=300, null=True)),
                ('classification_of_diseases', models.ForeignKey(to='patient.ClassificationOfDiseases')),
            ],
        ),
        migrations.CreateModel(
            name='ExamFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.FileField(upload_to=patient.models.get_user_dir)),
                ('exam', models.ForeignKey(to='patient.ComplementaryExam')),
            ],
        ),
        migrations.CreateModel(
            name='FleshTone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalPatient',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('name', models.CharField(max_length=50)),
                ('cpf', models.CharField(validators=[patient.models.validate_cpf], max_length=15, db_index=True, null=True, blank=True)),
                ('origin', models.CharField(max_length=50, null=True, blank=True)),
                ('medical_record', models.CharField(max_length=25, null=True, blank=True)),
                ('date_birth', models.DateField(validators=[patient.models.validate_date_birth])),
                ('rg', models.CharField(max_length=15, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
                ('zipcode', models.CharField(max_length=12, null=True, blank=True)),
                ('street', models.CharField(max_length=50, null=True, blank=True)),
                ('address_number', models.IntegerField(max_length=6, null=True, blank=True)),
                ('address_complement', models.CharField(max_length=50, null=True, blank=True)),
                ('district', models.CharField(max_length=50, null=True, blank=True)),
                ('city', models.CharField(max_length=30, null=True, blank=True)),
                ('state', models.CharField(max_length=30, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('removed', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, db_constraint=False, related_name='+', blank=True)),
                ('gender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Gender', db_constraint=False, related_name='+', blank=True)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical patient',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSocialDemographicData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('natural_of', models.CharField(max_length=50, null=True, blank=True)),
                ('citizenship', models.CharField(max_length=50, null=True, blank=True)),
                ('profession', models.CharField(max_length=50, null=True, blank=True)),
                ('occupation', models.CharField(max_length=50, null=True, blank=True)),
                ('benefit_government', models.NullBooleanField()),
                ('tv', models.IntegerField(null=True, blank=True)),
                ('dvd', models.IntegerField(null=True, blank=True)),
                ('radio', models.IntegerField(null=True, blank=True)),
                ('bath', models.IntegerField(null=True, blank=True)),
                ('automobile', models.IntegerField(null=True, blank=True)),
                ('wash_machine', models.IntegerField(null=True, blank=True)),
                ('refrigerator', models.IntegerField(null=True, blank=True)),
                ('freezer', models.IntegerField(null=True, blank=True)),
                ('house_maid', models.IntegerField(null=True, blank=True)),
                ('social_class', models.CharField(max_length=10, null=True, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, db_constraint=False, related_name='+', blank=True)),
                ('flesh_tone', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.FleshTone', db_constraint=False, related_name='+', blank=True)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical social demographic data',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSocialHistoryData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('smoker', models.NullBooleanField()),
                ('ex_smoker', models.NullBooleanField()),
                ('alcoholic', models.NullBooleanField()),
                ('drugs', models.CharField(max_length=25, null=True, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('alcohol_frequency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.AlcoholFrequency', db_constraint=False, related_name='+', blank=True)),
                ('alcohol_period', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.AlcoholPeriod', db_constraint=False, related_name='+', blank=True)),
                ('amount_cigarettes', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.AmountCigarettes', db_constraint=False, related_name='+', blank=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, db_constraint=False, related_name='+', blank=True)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical social history data',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTelephone',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('number', models.CharField(max_length=15)),
                ('type', models.CharField(choices=[('MO', 'Celular'), ('HO', 'Residencial'), ('WO', 'Comercial'), ('MA', 'Principal'), ('FW', 'Fax comercial'), ('FH', 'Fax residencial'), ('PA', 'Pager'), ('OT', 'Outros')], max_length=15, blank=True)),
                ('note', models.CharField(max_length=50, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, db_constraint=False, related_name='+', blank=True)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical telephone',
            },
        ),
        migrations.CreateModel(
            name='MaritalStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MedicalRecordData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'permissions': (('view_medicalrecorddata', 'Can view medical record'),),
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('cpf', models.CharField(validators=[patient.models.validate_cpf], blank=True, max_length=15, null=True, unique=True)),
                ('origin', models.CharField(max_length=50, null=True, blank=True)),
                ('medical_record', models.CharField(max_length=25, null=True, blank=True)),
                ('date_birth', models.DateField(validators=[patient.models.validate_date_birth])),
                ('rg', models.CharField(max_length=15, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
                ('zipcode', models.CharField(max_length=12, null=True, blank=True)),
                ('street', models.CharField(max_length=50, null=True, blank=True)),
                ('address_number', models.IntegerField(max_length=6, null=True, blank=True)),
                ('address_complement', models.CharField(max_length=50, null=True, blank=True)),
                ('district', models.CharField(max_length=50, null=True, blank=True)),
                ('city', models.CharField(max_length=30, null=True, blank=True)),
                ('state', models.CharField(max_length=30, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('removed', models.BooleanField(default=False)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('gender', models.ForeignKey(to='patient.Gender')),
                ('marital_status', models.ForeignKey(null=True, to='patient.MaritalStatus', blank=True)),
            ],
            options={
                'permissions': (('view_patient', 'Can view patient'),),
            },
        ),
        migrations.CreateModel(
            name='Payment',
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
                ('date', models.DateField(validators=[patient.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('patient', models.ForeignKey(to='patient.Patient')),
                ('questionnaire_responsible', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey')),
            ],
            options={
                'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),),
            },
        ),
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Schooling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SocialDemographicData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('natural_of', models.CharField(max_length=50, null=True, blank=True)),
                ('citizenship', models.CharField(max_length=50, null=True, blank=True)),
                ('profession', models.CharField(max_length=50, null=True, blank=True)),
                ('occupation', models.CharField(max_length=50, null=True, blank=True)),
                ('benefit_government', models.NullBooleanField()),
                ('tv', models.IntegerField(null=True, blank=True)),
                ('dvd', models.IntegerField(null=True, blank=True)),
                ('radio', models.IntegerField(null=True, blank=True)),
                ('bath', models.IntegerField(null=True, blank=True)),
                ('automobile', models.IntegerField(null=True, blank=True)),
                ('wash_machine', models.IntegerField(null=True, blank=True)),
                ('refrigerator', models.IntegerField(null=True, blank=True)),
                ('freezer', models.IntegerField(null=True, blank=True)),
                ('house_maid', models.IntegerField(null=True, blank=True)),
                ('social_class', models.CharField(max_length=10, null=True, blank=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('flesh_tone', models.ForeignKey(null=True, to='patient.FleshTone', blank=True)),
                ('patient', models.ForeignKey(to='patient.Patient')),
                ('payment', models.ForeignKey(null=True, to='patient.Payment', blank=True)),
                ('religion', models.ForeignKey(null=True, to='patient.Religion', blank=True)),
                ('schooling', models.ForeignKey(null=True, to='patient.Schooling', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SocialHistoryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smoker', models.NullBooleanField()),
                ('ex_smoker', models.NullBooleanField()),
                ('alcoholic', models.NullBooleanField()),
                ('drugs', models.CharField(max_length=25, null=True, blank=True)),
                ('alcohol_frequency', models.ForeignKey(null=True, to='patient.AlcoholFrequency', default=0, blank=True)),
                ('alcohol_period', models.ForeignKey(null=True, to='patient.AlcoholPeriod', default=0, blank=True)),
                ('amount_cigarettes', models.ForeignKey(null=True, to='patient.AmountCigarettes', default=0, blank=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(to='patient.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='Telephone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15)),
                ('type', models.CharField(choices=[('MO', 'Celular'), ('HO', 'Residencial'), ('WO', 'Comercial'), ('MA', 'Principal'), ('FW', 'Fax comercial'), ('FH', 'Fax residencial'), ('PA', 'Pager'), ('OT', 'Outros')], max_length=15, blank=True)),
                ('note', models.CharField(max_length=50, blank=True)),
                ('changed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(to='patient.Patient')),
            ],
        ),
        migrations.AddField(
            model_name='medicalrecorddata',
            name='patient',
            field=models.ForeignKey(to='patient.Patient'),
        ),
        migrations.AddField(
            model_name='medicalrecorddata',
            name='record_responsible',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaltelephone',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Patient', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalsocialhistorydata',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Patient', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalsocialdemographicdata',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Patient', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalsocialdemographicdata',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Payment', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalsocialdemographicdata',
            name='religion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Religion', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalsocialdemographicdata',
            name='schooling',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.Schooling', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='marital_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='patient.MaritalStatus', db_constraint=False, related_name='+', blank=True),
        ),
        migrations.AddField(
            model_name='diagnosis',
            name='medical_record_data',
            field=models.ForeignKey(to='patient.MedicalRecordData'),
        ),
        migrations.AddField(
            model_name='complementaryexam',
            name='diagnosis',
            field=models.ForeignKey(to='patient.Diagnosis'),
        ),
        migrations.AlterUniqueTogether(
            name='diagnosis',
            unique_together=set([('medical_record_data', 'classification_of_diseases')]),
        ),
    ]
