# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Subject'
        db.create_table(u'experiment_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patient.Patient'])),
        ))
        db.send_create_signal(u'experiment', ['Subject'])

        # Adding model 'TimeUnit'
        db.create_table(u'experiment_timeunit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'experiment', ['TimeUnit'])

        # Adding model 'StimulusType'
        db.create_table(u'experiment_stimulustype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'experiment', ['StimulusType'])

        # Adding model 'ResearchProject'
        db.create_table(u'experiment_researchproject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1500)),
        ))
        db.send_create_signal(u'experiment', ['ResearchProject'])

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

        # Adding model 'Component'
        db.create_table(u'experiment_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identification', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Experiment'])),
            ('component_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'experiment', ['Component'])

        # Adding model 'Task'
        db.create_table(u'experiment_task', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('instruction_text', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'experiment', ['Task'])

        # Adding model 'Instruction'
        db.create_table(u'experiment_instruction', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'experiment', ['Instruction'])

        # Adding model 'Pause'
        db.create_table(u'experiment_pause', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('duration_unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.TimeUnit'], null=True, blank=True)),
        ))
        db.send_create_signal(u'experiment', ['Pause'])

        # Adding model 'Stimulus'
        db.create_table(u'experiment_stimulus', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('stimulus_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.StimulusType'])),
        ))
        db.send_create_signal(u'experiment', ['Stimulus'])

        # Adding model 'Questionnaire'
        db.create_table(u'experiment_questionnaire', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('lime_survey_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'experiment', ['Questionnaire'])

        # Adding model 'Sequence'
        db.create_table(u'experiment_sequence', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['experiment.Component'], unique=True, primary_key=True)),
            ('has_random_components', self.gf('django.db.models.fields.BooleanField')()),
            ('number_of_mandatory_components', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'experiment', ['Sequence'])

        # Adding model 'ComponentConfiguration'
        db.create_table(u'experiment_componentconfiguration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('number_of_repetitions', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_repetitions_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_repetitions_unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.TimeUnit'], null=True, blank=True)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(related_name='configuration', to=orm['experiment.Component'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['experiment.Component'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'experiment', ['ComponentConfiguration'])

        # Adding unique constraint on 'ComponentConfiguration', fields ['parent', 'order']
        db.create_unique(u'experiment_componentconfiguration', ['parent_id', 'order'])

        # Adding model 'Group'
        db.create_table(u'experiment_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Experiment'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('instruction', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('experimental_protocol', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.ComponentConfiguration'], null=True)),
        ))
        db.send_create_signal(u'experiment', ['Group'])

        # Adding M2M table for field classification_of_diseases on 'Group'
        m2m_table_name = db.shorten_name(u'experiment_group_classification_of_diseases')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm[u'experiment.group'], null=False)),
            ('classificationofdiseases', models.ForeignKey(orm[u'patient.classificationofdiseases'], null=False))
        ))
        db.create_unique(m2m_table_name, ['group_id', 'classificationofdiseases_id'])

        # Adding model 'SubjectOfGroup'
        db.create_table(u'experiment_subjectofgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Subject'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Group'])),
            ('consent_form', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'experiment', ['SubjectOfGroup'])

        # Adding unique constraint on 'SubjectOfGroup', fields ['subject', 'group']
        db.create_unique(u'experiment_subjectofgroup', ['subject_id', 'group_id'])

        # Adding model 'HistoricalQuestionnaireConfiguration'
        db.create_table(u'experiment_historicalquestionnaireconfiguration', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('lime_survey_id', self.gf('django.db.models.fields.IntegerField')()),
            ('group_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
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
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.Group'], on_delete=models.PROTECT)),
            ('number_of_fills', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('interval_between_fills_unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.TimeUnit'], null=True, blank=True)),
        ))
        db.send_create_signal(u'experiment', ['QuestionnaireConfiguration'])

        # Adding unique constraint on 'QuestionnaireConfiguration', fields ['lime_survey_id', 'group']
        db.create_unique(u'experiment_questionnaireconfiguration', ['lime_survey_id', 'group_id'])

        # Adding model 'HistoricalQuestionnaireResponse'
        db.create_table(u'experiment_historicalquestionnaireresponse', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('subject_of_group_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
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
            ('subject_of_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.SubjectOfGroup'])),
            ('questionnaire_configuration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['experiment.QuestionnaireConfiguration'], on_delete=models.PROTECT)),
            ('token_id', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('questionnaire_responsible', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'experiment', ['QuestionnaireResponse'])


    def backwards(self, orm):
        # Removing unique constraint on 'QuestionnaireConfiguration', fields ['lime_survey_id', 'group']
        db.delete_unique(u'experiment_questionnaireconfiguration', ['lime_survey_id', 'group_id'])

        # Removing unique constraint on 'SubjectOfGroup', fields ['subject', 'group']
        db.delete_unique(u'experiment_subjectofgroup', ['subject_id', 'group_id'])

        # Removing unique constraint on 'ComponentConfiguration', fields ['parent', 'order']
        db.delete_unique(u'experiment_componentconfiguration', ['parent_id', 'order'])

        # Deleting model 'Subject'
        db.delete_table(u'experiment_subject')

        # Deleting model 'TimeUnit'
        db.delete_table(u'experiment_timeunit')

        # Deleting model 'StimulusType'
        db.delete_table(u'experiment_stimulustype')

        # Deleting model 'ResearchProject'
        db.delete_table(u'experiment_researchproject')

        # Deleting model 'HistoricalExperiment'
        db.delete_table(u'experiment_historicalexperiment')

        # Deleting model 'Experiment'
        db.delete_table(u'experiment_experiment')

        # Deleting model 'Component'
        db.delete_table(u'experiment_component')

        # Deleting model 'Task'
        db.delete_table(u'experiment_task')

        # Deleting model 'Instruction'
        db.delete_table(u'experiment_instruction')

        # Deleting model 'Pause'
        db.delete_table(u'experiment_pause')

        # Deleting model 'Stimulus'
        db.delete_table(u'experiment_stimulus')

        # Deleting model 'Questionnaire'
        db.delete_table(u'experiment_questionnaire')

        # Deleting model 'Sequence'
        db.delete_table(u'experiment_sequence')

        # Deleting model 'ComponentConfiguration'
        db.delete_table(u'experiment_componentconfiguration')

        # Deleting model 'Group'
        db.delete_table(u'experiment_group')

        # Removing M2M table for field classification_of_diseases on 'Group'
        db.delete_table(db.shorten_name(u'experiment_group_classification_of_diseases'))

        # Deleting model 'SubjectOfGroup'
        db.delete_table(u'experiment_subjectofgroup')

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
        u'experiment.component': {
            'Meta': {'object_name': 'Component'},
            'component_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identification': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.componentconfiguration': {
            'Meta': {'unique_together': "(('parent', 'order'),)", 'object_name': 'ComponentConfiguration'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'configuration'", 'to': u"orm['experiment.Component']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_between_repetitions_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.TimeUnit']", 'null': 'True', 'blank': 'True'}),
            'interval_between_repetitions_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'number_of_repetitions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['experiment.Component']"})
        },
        u'experiment.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.group': {
            'Meta': {'object_name': 'Group'},
            'classification_of_diseases': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['patient.ClassificationOfDiseases']", 'null': 'True', 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']"}),
            'experimental_protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.ComponentConfiguration']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instruction': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
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
            'group_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
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
            'subject_of_group_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.instruction': {
            'Meta': {'object_name': 'Instruction', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'experiment.pause': {
            'Meta': {'object_name': 'Pause', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'duration_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.TimeUnit']", 'null': 'True', 'blank': 'True'})
        },
        u'experiment.questionnaire': {
            'Meta': {'object_name': 'Questionnaire', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.questionnaireconfiguration': {
            'Meta': {'unique_together': "(('lime_survey_id', 'group'),)", 'object_name': 'QuestionnaireConfiguration'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Group']", 'on_delete': 'models.PROTECT'}),
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
            'subject_of_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.SubjectOfGroup']"}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.researchproject': {
            'Meta': {'object_name': 'ResearchProject'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'experiment.sequence': {
            'Meta': {'object_name': 'Sequence', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'has_random_components': ('django.db.models.fields.BooleanField', [], {}),
            'number_of_mandatory_components': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.stimulus': {
            'Meta': {'object_name': 'Stimulus', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'stimulus_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.StimulusType']"})
        },
        u'experiment.stimulustype': {
            'Meta': {'object_name': 'StimulusType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'experiment.subject': {
            'Meta': {'object_name': 'Subject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"})
        },
        u'experiment.subjectofgroup': {
            'Meta': {'unique_together': "(('subject', 'group'),)", 'object_name': 'SubjectOfGroup'},
            'consent_form': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Subject']"})
        },
        u'experiment.task': {
            'Meta': {'object_name': 'Task', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'instruction_text': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'experiment.timeunit': {
            'Meta': {'ordering': "['id']", 'object_name': 'TimeUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'patient.classificationofdiseases': {
            'Meta': {'object_name': 'ClassificationOfDiseases'},
            'abbreviated_description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'children'", 'null': 'True', 'to': u"orm['patient.ClassificationOfDiseases']"})
        },
        u'patient.gender': {
            'Meta': {'object_name': 'Gender'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.maritalstatus': {
            'Meta': {'object_name': 'MaritalStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.patient': {
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
            'gender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Gender']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marital_status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.MaritalStatus']", 'null': 'True', 'blank': 'True'}),
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