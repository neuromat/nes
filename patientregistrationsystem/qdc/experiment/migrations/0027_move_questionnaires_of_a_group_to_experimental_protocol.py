# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from experiment.abc_search_engine import Questionnaires


class Migration(DataMigration):

    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        list_of_distinct_group_ids =\
            [qc[0] for qc in orm.QuestionnaireConfiguration.objects.order_by().values_list('group_id').distinct()]

        for group_id in list_of_distinct_group_ids:
            group = orm.Group.objects.get(id=group_id)

            # Create a new block that will become the root of the experimental protocol of the group. All questionnaires
            # of the group will become a child of this block.
            block = orm.Block()
            block.identification = 'Root of the protocol for ' + group.title[:25]
            block.description = 'This block was created to allow the migration of one or more questionnaires from ' \
                                'the group to the experimental protocol of the group.'
            block.experiment = group.experiment
            block.component_type = 'block'
            block.type = 'parallel_block'
            block.save()

            next_order = 1

            if group.experimental_protocol is not None:
                # Use the current root of the experimental protocol as a child of the created block
                cc2 = orm.ComponentConfiguration()
                cc2.component = group.experimental_protocol
                cc2.parent = block
                cc2.order = next_order
                next_order += 1
                cc2.number_of_repetitions = 1
                cc2.save()

            # Use the created block as the experimental protocol of the group
            group.experimental_protocol = block
            group.save()

            # Migration of the questionnaires (QuestionnaireConfiguration) of the group.
            for qc in orm.QuestionnaireConfiguration.objects.filter(group_id=group_id):
                # Create a questionnaire
                questionnaire = orm.Questionnaire()
                # Use the first 50 characters of the name of the survey as the identification of the component.
                questionnaire.identification = "LimeSurvey ID " + str(qc.lime_survey_id)
                questionnaire.description = 'This questionnaire was migrated from the group to the experimental ' \
                                            'protocol of the group.'
                questionnaire.experiment = group.experiment
                questionnaire.component_type = 'questionnaire'
                questionnaire.lime_survey_id = qc.lime_survey_id
                questionnaire.used_also_outside_an_experiment = False
                questionnaire.save()

                # Use the created questionnaire as a child of the created block
                cc = orm.ComponentConfiguration()
                cc.component = questionnaire
                cc.parent = block
                cc.order = next_order
                next_order += 1
                # There is no need to set the flag random_position in a parallel block.
                cc.number_of_repetitions = qc.number_of_fills
                cc.interval_between_repetitions_value = qc.interval_between_fills_value
                cc.interval_between_repetitions_unit = qc.interval_between_fills_unit
                cc.save()

                # Migration of the responses
                for qr in orm.QuestionnaireResponse.objects.filter(questionnaire_configuration=qc):
                    qr.component_configuration = cc
                    qr.save()

    def backwards(self, orm):
        # Problems with this backwards:
        # 1. QuestionnaireConfigurations that used to be in the group before the forwards but does not have responses
        # are lost. A possible solution is to create a QuestionnaireConfiguration for each Questinnaire component
        # reachable from the root of the experimental protocol, then complement this set by including those that have
        # responses but are not in the experimental protocol any longer.
        # 2. ComponentConfiguration that are created in forwards are not deleted. This causes duplication of
        # ComponentConfigurations when running forwards more than once. A possible solution is to delete all
        # ComponentConfigurations that are Questionnaires. Blocks that become single child should also be deleted
        # and their children should become children of the parent of the erased block.

        # For each questionnaire response that doesn't have a questionnaire configuration, assign the questionnaire
        # configuration associated with the component and group. If it doesn't exists, create one.
        for qr in orm.QuestionnaireResponse.objects.all():
            if qr.questionnaire_configuration is None:
                q = orm.Questionnaire.objects.get(id=qr.component_configuration.component.id)
                try:
                    qc = orm.QuestionnaireConfiguration.objects.get(group_id=qr.subject_of_group.group.id,
                                                                    lime_survey_id=q.lime_survey_id)
                except orm.QuestionnaireConfiguration.DoesNotExist:
                    qc = orm.QuestionnaireConfiguration()
                    qc.lime_survey_id = q.lime_survey_id
                    qc.group_id = qr.subject_of_group.group.id
                    qc.save()

                qr.questionnaire_configuration = qc
                qr.save()

        # To avoid problems in migration 0010_auto__chg_field_group_experimental_protocol, we delete the experimental
        # protocol of all groups.
        for group in orm.Group.objects.all():
            group.experimental_protocol = None
            group.save()

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
        u'experiment.block': {
            'Meta': {'object_name': 'Block', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'number_of_mandatory_components': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'experiment.component': {
            'Meta': {'object_name': 'Component'},
            'component_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration_unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'duration_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identification': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.componentconfiguration': {
            'Meta': {'unique_together': "(('parent', 'order'),)", 'object_name': 'ComponentConfiguration'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'configuration'", 'to': u"orm['experiment.Component']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_between_repetitions_unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'interval_between_repetitions_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'number_of_repetitions': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['experiment.Block']"}),
            'random_position': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'research_project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.ResearchProject']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'experiment.group': {
            'Meta': {'object_name': 'Group'},
            'classification_of_diseases': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['patient.ClassificationOfDiseases']", 'null': 'True', 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Experiment']"}),
            'experimental_protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Component']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.historicalexperiment': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalExperiment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'research_project_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'experiment.historicalquestionnaireconfiguration': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalQuestionnaireConfiguration'},
            'group_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'interval_between_fills_unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'interval_between_fills_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_fills': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.historicalquestionnaireresponse': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalQuestionnaireResponse'},
            'component_configuration_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
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
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'experiment.keyword': {
            'Meta': {'object_name': 'Keyword'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'experiment.patientquestionnaireresponse': {
            'Meta': {'object_name': 'PatientQuestionnaireResponse'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Questionnaire']"}),
            'questionnaire_responsible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.pause': {
            'Meta': {'object_name': 'Pause', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'experiment.questionnaire': {
            'Meta': {'object_name': 'Questionnaire', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {}),
            'used_also_outside_an_experiment': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'experiment.questionnaireconfiguration': {
            'Meta': {'unique_together': "(('lime_survey_id', 'group'),)", 'object_name': 'QuestionnaireConfiguration'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.Group']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_between_fills_unit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'interval_between_fills_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lime_survey_id': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_fills': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'experiment.questionnaireresponse': {
            'Meta': {'object_name': 'QuestionnaireResponse'},
            'component_configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.ComponentConfiguration']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questionnaire_configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.QuestionnaireConfiguration']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'questionnaire_responsible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'subject_of_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['experiment.SubjectOfGroup']"}),
            'token_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'experiment.researchproject': {
            'Meta': {'object_name': 'ResearchProject'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['experiment.Keyword']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'experiment.taskfortheexperimenter': {
            'Meta': {'object_name': 'TaskForTheExperimenter', '_ormbases': [u'experiment.Component']},
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['experiment.Component']", 'unique': 'True', 'primary_key': 'True'})
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
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
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
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['experiment']
    symmetrical = True
