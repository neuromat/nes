# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("patient", "0002_load_data_from_quiz.py"),
    )

    def forwards(self, orm):
        # Removing unique constraint on 'Diagnosis', fields ['medical_record_data', 'classification_of_diseases']
        db.delete_unique(u'quiz_diagnosis', ['medical_record_data_id', 'classification_of_diseases_id'])

        # Deleting model 'HistoricalPatient'
        db.delete_table(u'quiz_historicalpatient')

        # Deleting model 'SocialDemographicData'
        db.delete_table(u'quiz_socialdemographicdata')

        # Deleting model 'ComplementaryExam'
        db.delete_table(u'quiz_complementaryexam')

        # Deleting model 'MaritalStatus'
        db.delete_table(u'quiz_maritalstatus')

        # Deleting model 'SocialHistoryData'
        db.delete_table(u'quiz_socialhistorydata')

        # Deleting model 'ExamFile'
        db.delete_table(u'quiz_examfile')

        # Deleting model 'Religion'
        db.delete_table(u'quiz_religion')

        # Deleting model 'MedicalRecordData'
        db.delete_table(u'quiz_medicalrecorddata')

        # Deleting model 'AlcoholFrequency'
        db.delete_table(u'quiz_alcoholfrequency')

        # Deleting model 'Payment'
        db.delete_table(u'quiz_payment')

        # Deleting model 'HistoricalSocialDemographicData'
        db.delete_table(u'quiz_historicalsocialdemographicdata')

        # Deleting model 'HistoricalSocialHistoryData'
        db.delete_table(u'quiz_historicalsocialhistorydata')

        # Deleting model 'Gender'
        db.delete_table(u'quiz_gender')

        # Deleting model 'AlcoholPeriod'
        db.delete_table(u'quiz_alcoholperiod')

        # Deleting model 'AmountCigarettes'
        db.delete_table(u'quiz_amountcigarettes')

        # Deleting model 'ClassificationOfDiseases'
        db.delete_table(u'quiz_classificationofdiseases')

        # Deleting model 'Schooling'
        db.delete_table(u'quiz_schooling')

        # Deleting model 'Diagnosis'
        db.delete_table(u'quiz_diagnosis')

        # Deleting model 'Patient'
        db.delete_table(u'quiz_patient')

        # Deleting model 'FleshTone'
        db.delete_table(u'quiz_fleshtone')


    def backwards(self, orm):
        # Adding model 'HistoricalPatient'
        db.create_table(u'quiz_historicalpatient', (
            ('citizenship', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_number', self.gf('django.db.models.fields.IntegerField')(max_length=6, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('medical_record', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('natural_of', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('marital_status_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('cellphone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('date_birth', self.gf('django.db.models.fields.DateField')()),
            ('address_complement', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(blank=True, max_length=15, null=True, db_index=True)),
            ('gender_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalPatient'])

        # Adding model 'SocialDemographicData'
        db.create_table(u'quiz_socialdemographicdata', (
            ('wash_machine', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('flesh_tone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.FleshTone'], null=True, blank=True)),
            ('tv', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('automobile', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('house_maid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('schooling', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Schooling'], null=True, blank=True)),
            ('freezer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bath', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('religion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Religion'], null=True, blank=True)),
            ('radio', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Payment'], null=True, blank=True)),
            ('dvd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('social_class', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('refrigerator', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('benefit_government', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'quiz', ['SocialDemographicData'])

        # Adding model 'ComplementaryExam'
        db.create_table(u'quiz_complementaryexam', (
            ('doctor_register', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('diagnosis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Diagnosis'])),
            ('doctor', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('exam_site', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quiz', ['ComplementaryExam'])

        # Adding model 'MaritalStatus'
        db.create_table(u'quiz_maritalstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['MaritalStatus'])

        # Adding model 'SocialHistoryData'
        db.create_table(u'quiz_socialhistorydata', (
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            ('amount_cigarettes', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AmountCigarettes'], null=True, blank=True)),
            ('alcoholic', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('drugs', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('ex_smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcohol_frequency', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AlcoholFrequency'], null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcohol_period', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AlcoholPeriod'], null=True, blank=True)),
        ))
        db.send_create_signal(u'quiz', ['SocialHistoryData'])

        # Adding model 'ExamFile'
        db.create_table(u'quiz_examfile', (
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.ComplementaryExam'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quiz', ['ExamFile'])

        # Adding model 'Religion'
        db.create_table(u'quiz_religion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Religion'])

        # Adding model 'MedicalRecordData'
        db.create_table(u'quiz_medicalrecorddata', (
            ('record_responsible', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'quiz', ['MedicalRecordData'])

        # Adding model 'AlcoholFrequency'
        db.create_table(u'quiz_alcoholfrequency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'quiz', ['AlcoholFrequency'])

        # Adding model 'Payment'
        db.create_table(u'quiz_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Payment'])

        # Adding model 'HistoricalSocialDemographicData'
        db.create_table(u'quiz_historicalsocialdemographicdata', (
            ('flesh_tone_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('bath', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('radio', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('schooling_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('tv', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('automobile', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('freezer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('benefit_government', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('house_maid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wash_machine', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('refrigerator', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('payment_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('dvd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('patient_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('religion_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('social_class', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalSocialDemographicData'])

        # Adding model 'HistoricalSocialHistoryData'
        db.create_table(u'quiz_historicalsocialhistorydata', (
            ('alcohol_frequency_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True, db_index=True)),
            ('drugs', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ex_smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            ('patient_id', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True, db_index=True)),
            (u'id', self.gf('django.db.models.fields.IntegerField')(blank=True, db_index=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('alcoholic', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcohol_period_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True, db_index=True)),
            ('amount_cigarettes_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True, db_index=True)),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalSocialHistoryData'])

        # Adding model 'Gender'
        db.create_table(u'quiz_gender', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Gender'])

        # Adding model 'AlcoholPeriod'
        db.create_table(u'quiz_alcoholperiod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['AlcoholPeriod'])

        # Adding model 'AmountCigarettes'
        db.create_table(u'quiz_amountcigarettes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['AmountCigarettes'])

        # Adding model 'ClassificationOfDiseases'
        db.create_table(u'quiz_classificationofdiseases', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'children', null=True, to=orm['quiz.ClassificationOfDiseases'])),
            ('abbreviated_description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quiz', ['ClassificationOfDiseases'])

        # Adding model 'Schooling'
        db.create_table(u'quiz_schooling', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Schooling'])

        # Adding model 'Diagnosis'
        db.create_table(u'quiz_diagnosis', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300, null=True)),
            ('medical_record_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.MedicalRecordData'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('classification_of_diseases', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.ClassificationOfDiseases'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'quiz', ['Diagnosis'])

        # Adding unique constraint on 'Diagnosis', fields ['medical_record_data', 'classification_of_diseases']
        db.create_unique(u'quiz_diagnosis', ['medical_record_data_id', 'classification_of_diseases_id'])

        # Adding model 'Patient'
        db.create_table(u'quiz_patient', (
            ('citizenship', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_number', self.gf('django.db.models.fields.IntegerField')(max_length=6, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('medical_record', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('natural_of', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('cellphone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('date_birth', self.gf('django.db.models.fields.DateField')()),
            ('address_complement', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('marital_status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.MaritalStatus'], null=True, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Gender'])),
        ))
        db.send_create_signal(u'quiz', ['Patient'])

        # Adding model 'FleshTone'
        db.create_table(u'quiz_fleshtone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['FleshTone'])


    models = {
        
    }

    complete_apps = ['quiz']