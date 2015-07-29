# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("quiz", "0001_initial.py"),
    )

    def forwards(self, orm):
        # Adding model 'Subject'
        db.create_table(u'experiment_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Patient'])),
        ))
        db.send_create_signal(u'experiment', ['Subject'])

        # Adding model 'TimeUnit'
        db.create_table(u'experiment_timeunit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'experiment', ['TimeUnit'])

        # Adding model 'HistoricalExperiment'
        db.create_table(u'experiment_historicalexperiment', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'experiment', ['HistoricalExperiment'])

        # Adding model 'Experiment'
        db.create_table(u'experiment_experiment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'experiment', ['Experiment'])

        # Adding model 'SubjectOfExperiment'
        db.create_table(u'experiment_subjectofexperiment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Subject'])),
            ('experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Experiment'])),
            ('consent_form', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'experiment', ['SubjectOfExperiment'])

        # Adding unique constraint on 'SubjectOfExperiment', fields ['subject', 'experiment']
        db.create_unique(u'experiment_subjectofexperiment', ['subject_id', 'experiment_id'])

        # Adding model 'HistoricalQuestionnaireConfiguration'
        db.create_table(u'experiment_historicalquestionnaireconfiguration', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('lime_survey_id', self.gf('django.db.models.fields.IntegerField')()),
            ('experiment_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('number_of_fills', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_unit_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'experiment', ['HistoricalQuestionnaireConfiguration'])

        # Adding model 'QuestionnaireConfiguration'
        db.create_table(u'experiment_questionnaireconfiguration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lime_survey_id', self.gf('django.db.models.fields.IntegerField')()),
            ('experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Experiment'], on_delete=models.PROTECT)),
            ('number_of_fills', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.TimeUnit'], null=True, blank=True)),
        ))
        db.send_create_signal(u'experiment', ['QuestionnaireConfiguration'])

        # Adding unique constraint on 'QuestionnaireConfiguration', fields ['lime_survey_id', 'experiment']
        db.create_unique(u'experiment_questionnaireconfiguration', ['lime_survey_id', 'experiment_id'])

        # Adding model 'HistoricalQuestionnaireResponse'
        db.create_table(u'experiment_historicalquestionnaireresponse', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('subject_of_experiment_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('questionnaire_configuration_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('token_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('questionnaire_responsible_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'experiment', ['HistoricalQuestionnaireResponse'])

        # Adding model 'QuestionnaireResponse'
        db.create_table(u'experiment_questionnaireresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject_of_experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.SubjectOfExperiment'])),
            ('questionnaire_configuration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.QuestionnaireConfiguration'], on_delete=models.PROTECT)),
            ('token_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('questionnaire_responsible', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'experiment', ['QuestionnaireResponse'])


    def backwards(self, orm):
        # Removing unique constraint on 'QuestionnaireConfiguration', fields ['lime_survey_id', 'experiment']
        db.delete_unique(u'experiment_questionnaireconfiguration', ['lime_survey_id', 'experiment_id'])

        # Removing unique constraint on 'SubjectOfExperiment', fields ['subject', 'experiment']
        db.delete_unique(u'experiment_subjectofexperiment', ['subject_id', 'experiment_id'])

        # Deleting model 'Subject'
        db.delete_table(u'experiment_subject')

        # Deleting model 'TimeUnit'
        db.delete_table(u'experiment_timeunit')

        # Deleting model 'HistoricalExperiment'
        db.delete_table(u'experiment_historicalexperiment')

        # Deleting model 'Experiment'
        db.delete_table(u'experiment_experiment')

        # Deleting model 'SubjectOfExperiment'
        db.delete_table(u'experiment_subjectofexperiment')

        # Deleting model 'HistoricalQuestionnaireConfiguration'
        db.delete_table(u'experiment_historicalquestionnaireconfiguration')

        # Deleting model 'QuestionnaireConfiguration'
        db.delete_table(u'experiment_questionnaireconfiguration')

        # Deleting model 'HistoricalQuestionnaireResponse'
        db.delete_table(u'experiment_historicalquestionnaireresponse')

        # Deleting model 'QuestionnaireResponse'
        db.delete_table(u'experiment_questionnaireresponse')


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
        u'experiment.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.historicalexperiment': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalExperiment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.historicalquestionnaireconfiguration': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalQuestionnaireConfiguration'},
            'experiment_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'interval_between_fills_unit_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'interval_between_fills_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_fills': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.historicalquestionnaireresponse': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalQuestionnaireResponse'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'questionnaire_configuration_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'questionnaire_responsible_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'subject_of_experiment_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.questionnaireconfiguration': {
            'Meta': {'unique_together': "(('lime_survey_id', 'experiment'),)", 'object_name': 'QuestionnaireConfiguration'},
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_between_fills_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.TimeUnit']", 'null': 'True', 'blank': 'True'}),
            'interval_between_fills_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_fills': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.questionnaireresponse': {
            'Meta': {'object_name': 'QuestionnaireResponse'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questionnaire_configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.QuestionnaireConfiguration']", 'on_delete': 'models.PROTECT'}),
            'questionnaire_responsible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'subject_of_experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.SubjectOfExperiment']"}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.subject': {
            'Meta': {'object_name': 'Subject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quiz.Patient']"})
        },
        u'experiment.subjectofexperiment': {
            'Meta': {'unique_together': "(('subject', 'experiment'),)", 'object_name': 'SubjectOfExperiment'},
            'consent_form': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Subject']"})
        },
        u'experiment.timeunit': {
            'Meta': {'ordering': "['id']", 'object_name': 'TimeUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'quiz.gender': {
            'Meta': {'object_name': 'Gender'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'quiz.maritalstatus': {
            'Meta': {'object_name': 'MaritalStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        }
    }

    complete_apps = ['experiment']