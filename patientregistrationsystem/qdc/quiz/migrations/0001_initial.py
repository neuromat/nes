# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Payment'
        db.create_table(u'quiz_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Payment'])

        # Adding model 'Gender'
        db.create_table(u'quiz_gender', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Gender'])

        # Adding model 'FleshTone'
        db.create_table(u'quiz_fleshtone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['FleshTone'])

        # Adding model 'MaritalStatus'
        db.create_table(u'quiz_maritalstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['MaritalStatus'])

        # Adding model 'Religion'
        db.create_table(u'quiz_religion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Religion'])

        # Adding model 'Schooling'
        db.create_table(u'quiz_schooling', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['Schooling'])

        # Adding model 'AmountCigarettes'
        db.create_table(u'quiz_amountcigarettes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['AmountCigarettes'])

        # Adding model 'AlcoholFrequency'
        db.create_table(u'quiz_alcoholfrequency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'quiz', ['AlcoholFrequency'])

        # Adding model 'AlcoholPeriod'
        db.create_table(u'quiz_alcoholperiod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'quiz', ['AlcoholPeriod'])

        # Adding model 'HistoricalPatient'
        db.create_table(u'quiz_historicalpatient', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=15, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('medical_record', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('natural_of', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('citizenship', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_number', self.gf('django.db.models.fields.IntegerField')(max_length=6, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('cellphone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('date_birth', self.gf('django.db.models.fields.DateField')()),
            ('gender_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('marital_status_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalPatient'])

        # Adding model 'Patient'
        db.create_table(u'quiz_patient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(max_length=15, unique=True, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('medical_record', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('natural_of', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('citizenship', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_number', self.gf('django.db.models.fields.IntegerField')(max_length=6, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('cellphone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('date_birth', self.gf('django.db.models.fields.DateField')()),
            ('gender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Gender'])),
            ('marital_status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.MaritalStatus'], null=True, blank=True)),
            ('removed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'quiz', ['Patient'])

        # Adding model 'HistoricalSocialDemographicData'
        db.create_table(u'quiz_historicalsocialdemographicdata', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('patient_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('religion_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('benefit_government', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('payment_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('flesh_tone_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('schooling_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('tv', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('dvd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('radio', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bath', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('automobile', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('wash_machine', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('refrigerator', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('freezer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('house_maid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('social_class', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalSocialDemographicData'])

        # Adding model 'SocialDemographicData'
        db.create_table(u'quiz_socialdemographicdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            ('religion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Religion'], null=True, blank=True)),
            ('profession', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('occupation', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('benefit_government', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Payment'], null=True, blank=True)),
            ('flesh_tone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.FleshTone'], null=True, blank=True)),
            ('schooling', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Schooling'], null=True, blank=True)),
            ('tv', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('dvd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('radio', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bath', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('automobile', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('wash_machine', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('refrigerator', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('freezer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('house_maid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('social_class', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'quiz', ['SocialDemographicData'])

        # Adding model 'HistoricalSocialHistoryData'
        db.create_table(u'quiz_historicalsocialhistorydata', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('patient_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('amount_cigarettes_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_index=True, blank=True)),
            ('ex_smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcoholic', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcohol_frequency_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_index=True, blank=True)),
            ('alcohol_period_id', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_index=True, blank=True)),
            ('drugs', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('changed_by_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'quiz', ['HistoricalSocialHistoryData'])

        # Adding model 'SocialHistoryData'
        db.create_table(u'quiz_socialhistorydata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            ('smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('amount_cigarettes', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AmountCigarettes'], null=True, blank=True)),
            ('ex_smoker', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcoholic', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('alcohol_frequency', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AlcoholFrequency'], null=True, blank=True)),
            ('alcohol_period', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['quiz.AlcoholPeriod'], null=True, blank=True)),
            ('drugs', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'quiz', ['SocialHistoryData'])

        # Adding model 'MedicalRecordData'
        db.create_table(u'quiz_medicalrecorddata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
            ('record_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('record_responsible', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'quiz', ['MedicalRecordData'])

        # Adding model 'ClassificationOfDiseases'
        db.create_table(u'quiz_classificationofdiseases', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('abbreviated_description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'children', null=True, to=orm['quiz.ClassificationOfDiseases'])),
        ))
        db.send_create_signal(u'quiz', ['ClassificationOfDiseases'])

        # Adding model 'Diagnosis'
        db.create_table(u'quiz_diagnosis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medical_record_data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.MedicalRecordData'])),
            ('classification_of_diseases', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.ClassificationOfDiseases'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300, null=True)),
        ))
        db.send_create_signal(u'quiz', ['Diagnosis'])

        # Adding unique constraint on 'Diagnosis', fields ['medical_record_data', 'classification_of_diseases']
        db.create_unique(u'quiz_diagnosis', ['medical_record_data_id', 'classification_of_diseases_id'])

        # Adding model 'ComplementaryExam'
        db.create_table(u'quiz_complementaryexam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('diagnosis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Diagnosis'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('doctor', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('doctor_register', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('exam_site', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'quiz', ['ComplementaryExam'])

        # Adding model 'ExamFile'
        db.create_table(u'quiz_examfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exam', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.ComplementaryExam'])),
            ('content', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'quiz', ['ExamFile'])


    def backwards(self, orm):
        # Removing unique constraint on 'Diagnosis', fields ['medical_record_data', 'classification_of_diseases']
        db.delete_unique(u'quiz_diagnosis', ['medical_record_data_id', 'classification_of_diseases_id'])

        # Deleting model 'Payment'
        db.delete_table(u'quiz_payment')

        # Deleting model 'Gender'
        db.delete_table(u'quiz_gender')

        # Deleting model 'FleshTone'
        db.delete_table(u'quiz_fleshtone')

        # Deleting model 'MaritalStatus'
        db.delete_table(u'quiz_maritalstatus')

        # Deleting model 'Religion'
        db.delete_table(u'quiz_religion')

        # Deleting model 'Schooling'
        db.delete_table(u'quiz_schooling')

        # Deleting model 'AmountCigarettes'
        db.delete_table(u'quiz_amountcigarettes')

        # Deleting model 'AlcoholFrequency'
        db.delete_table(u'quiz_alcoholfrequency')

        # Deleting model 'AlcoholPeriod'
        db.delete_table(u'quiz_alcoholperiod')

        # Deleting model 'HistoricalPatient'
        db.delete_table(u'quiz_historicalpatient')

        # Deleting model 'Patient'
        db.delete_table(u'quiz_patient')

        # Deleting model 'HistoricalSocialDemographicData'
        db.delete_table(u'quiz_historicalsocialdemographicdata')

        # Deleting model 'SocialDemographicData'
        db.delete_table(u'quiz_socialdemographicdata')

        # Deleting model 'HistoricalSocialHistoryData'
        db.delete_table(u'quiz_historicalsocialhistorydata')

        # Deleting model 'SocialHistoryData'
        db.delete_table(u'quiz_socialhistorydata')

        # Deleting model 'MedicalRecordData'
        db.delete_table(u'quiz_medicalrecorddata')

        # Deleting model 'ClassificationOfDiseases'
        db.delete_table(u'quiz_classificationofdiseases')

        # Deleting model 'Diagnosis'
        db.delete_table(u'quiz_diagnosis')

        # Deleting model 'ComplementaryExam'
        db.delete_table(u'quiz_complementaryexam')

        # Deleting model 'ExamFile'
        db.delete_table(u'quiz_examfile')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quiz.alcoholfrequency': {
            'Meta': {'object_name': 'AlcoholFrequency'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quiz.alcoholperiod': {
            'Meta': {'object_name': 'AlcoholPeriod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.amountcigarettes': {
            'Meta': {'object_name': 'AmountCigarettes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.classificationofdiseases': {
            'Meta': {'object_name': 'ClassificationOfDiseases'},
            'abbreviated_description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'children'", 'null': 'True', 'to': u"orm['quiz.ClassificationOfDiseases']"})
        },
        u'quiz.complementaryexam': {
            'Meta': {'object_name': 'ComplementaryExam'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'diagnosis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Diagnosis']"}),
            'doctor': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'doctor_register': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'exam_site': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'quiz.diagnosis': {
            'Meta': {'unique_together': "((u'medical_record_data', u'classification_of_diseases'),)", 'object_name': 'Diagnosis'},
            'classification_of_diseases': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.ClassificationOfDiseases']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_record_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.MedicalRecordData']"})
        },
        u'quiz.examfile': {
            'Meta': {'object_name': 'ExamFile'},
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.ComplementaryExam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'quiz.fleshtone': {
            'Meta': {'object_name': 'FleshTone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.gender': {
            'Meta': {'object_name': 'Gender'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.historicalpatient': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalPatient'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.IntegerField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'citizenship': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'date_birth': ('django.db.models.fields.DateField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'gender_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'marital_status_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'medical_record': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'natural_of': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        },
        u'quiz.historicalsocialdemographicdata': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalSocialDemographicData'},
            'automobile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bath': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'benefit_government': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'dvd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flesh_tone_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'freezer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'house_maid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'payment_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refrigerator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'religion_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'schooling_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'social_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tv': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wash_machine': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'quiz.historicalsocialhistorydata': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalSocialHistoryData'},
            'alcohol_frequency_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'alcohol_period_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'alcoholic': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'amount_cigarettes_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'drugs': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'ex_smoker': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'smoker': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'quiz.maritalstatus': {
            'Meta': {'object_name': 'MaritalStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.medicalrecorddata': {
            'Meta': {'object_name': 'MedicalRecordData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Patient']"}),
            'record_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'record_responsible': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'quiz.patient': {
            'Meta': {'object_name': 'Patient'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.IntegerField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'citizenship': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'date_birth': ('django.db.models.fields.DateField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Gender']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marital_status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.MaritalStatus']", 'null': 'True', 'blank': 'True'}),
            'medical_record': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'natural_of': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        },
        u'quiz.payment': {
            'Meta': {'object_name': 'Payment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.religion': {
            'Meta': {'object_name': 'Religion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.schooling': {
            'Meta': {'object_name': 'Schooling'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.socialdemographicdata': {
            'Meta': {'object_name': 'SocialDemographicData'},
            'automobile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bath': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'benefit_government': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'dvd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flesh_tone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.FleshTone']", 'null': 'True', 'blank': 'True'}),
            'freezer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'house_maid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Patient']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Payment']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refrigerator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Religion']", 'null': 'True', 'blank': 'True'}),
            'schooling': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Schooling']", 'null': 'True', 'blank': 'True'}),
            'social_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tv': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wash_machine': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'quiz.socialhistorydata': {
            'Meta': {'object_name': 'SocialHistoryData'},
            'alcohol_frequency': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['quiz.AlcoholFrequency']", 'null': 'True', 'blank': 'True'}),
            'alcohol_period': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['quiz.AlcoholPeriod']", 'null': 'True', 'blank': 'True'}),
            'alcoholic': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'amount_cigarettes': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['quiz.AmountCigarettes']", 'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'drugs': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'ex_smoker': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Patient']"}),
            'smoker': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['quiz']