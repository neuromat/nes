import os
import io
import tempfile
import zipfile
from datetime import datetime

import shutil
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from experiment.models import Component, Subject, SubjectOfGroup
from experiment.tests_original import ObjectsFactory
from patient.tests import UtilTests
from qdc import settings
from survey.abc_search_engine import Questionnaires
from survey.models import Survey


class ExportQuestionnaireTest(TestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def get_lime_survey_question_groups(self, sid):
        question_groups_all = \
            [item for item in self.lime_survey.list_groups(sid)
             if item['language'] == 'en']
        question_groups = dict()
        for question_group_all in question_groups_all:
            question_groups[question_group_all['gid']] = \
                question_group_all['group_name']

        return question_groups

    def make_column_names(self, question_groups):
        column_names_dict = dict()
        for question_group in question_groups:
            for question_id \
                    in self.lime_survey.list_questions(self.sid,
                                                       question_group):
                key = \
                    self.lime_survey.get_question_properties(question_id,
                                                             'en')['title']
                column_names_dict[key] = \
                    str(self.sid) + 'X' + str(question_group) + 'X' + str(
                        question_id)

        return column_names_dict

    def get_limesurvey_table_question_codes(self):
        question_groups = self.get_lime_survey_question_groups(self.sid)
        column_names_dict = self.make_column_names(question_groups)

        return column_names_dict

    def setUp(self):
        exec(open('add_initial_data.py').read())
        self.user = User.objects.create_user(
            username='jose', email='jose@test.com', password='passwd'
        )
        user_profile = self.user.user_profile
        user_profile.login_enabled = True
        # this is necessary for surpass the middleware that forces password
        # change when login in first time
        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        # create experiment/experimental protocol/group
        self.experiment = ObjectsFactory.create_experiment(
            ObjectsFactory.create_research_project(self.user)
        )
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create subject of group
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = Subject.objects.create(patient=patient)
        self.subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=self.group
        )
        self.group.subjectofgroup_set.add(self.subject_of_group)

        # create questionnaire at LiveSurvey
        survey_title = 'Test questionnaire'
        self.lime_survey = Questionnaires()
        self.sid = self.lime_survey.add_survey(999999, survey_title, 'en', 'G')

        # create required group/questions for LimeSurvey/NES integration
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests',
                'NESIdentification_group.lsg'
        )) as file:
            content = file.read()
            self.lime_survey.insert_questions(self.sid, content, 'lsg')

        # create other group of questions/questions
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests', 'limesurvey_group_2.lsg'
        )) as file:
            content = file.read()
            self.lime_survey.insert_questions(self.sid, content, 'lsg')

        # activate survey and tokens
        self.lime_survey.activate_survey(self.sid)
        self.lime_survey.activate_tokens(self.sid)

        # create questionnaire in NES
        self.survey = Survey.objects.create(lime_survey_id=self.sid)
        # create questionnaire component
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'sid': self.survey.id}
        )

        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, questionnaire
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # add response to limesurvey survey and the references in our db
        result = UtilTests().create_survey_participant(self.survey)
        UtilTests().create_response_survey_mock(
            self.user, patient, self.survey, result['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject.id,
            response_table_columns['firstQuestion']: 'Olá Mundo!',
            response_table_columns['secondQuestion']: 'Hallo Welt!'
        }
        self.lime_survey.add_response(self.sid, response_data)

        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result['tid'],
            {'completed': datetime.utcnow().strftime('%Y-%m-%d')}
        )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=result['tid'],
            subject_of_group=self.subject_of_group
        )

    def tearDown(self):
        self.lime_survey.delete_survey(self.sid)
        self.client.logout()

    def test_same_questionnaire_used_in_different_steps_return_correct_zipfile_content(self):
        # TODO: testar com sobreposição do subdiretório media

        ##
        # Create component (step) QUESTIONNAIRE
        ##
        # create other component (step) QUESTIONNAIRE in same experimental
        # protocol
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'sid': self.survey.id}
        )
        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, questionnaire
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        ##
        # Create patient/subject/subject_of_group
        ##
        # create other subject of group
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = Subject.objects.create(patient=patient)
        subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=self.group
        )
        self.group.subjectofgroup_set.add(subject_of_group)

        ##
        # Add response to questionnaire in NES and LimeSurvey
        ##
        # add response to limesurvey survey and the references in our db
        result = UtilTests().create_survey_participant(self.survey)
        # TODO:
        # acho que não precisa criar resposta do participante enquanto
        # estamos testando resposta para experimento.
        UtilTests().create_response_survey_mock(
            self.user, patient, self.survey, result['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject.id,
            response_table_columns['firstQuestion']: 'Al mondo!',
            response_table_columns['secondQuestion']: 'Til verden!'
        }
        self.lime_survey.add_response(self.sid, response_data)
        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/
        # 113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result['tid'],
            {'completed': datetime.utcnow().strftime('%Y-%m-%d')}
        )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=result['tid'],
            subject_of_group=subject_of_group
        )

        ##
        # Post data to view
        ##
        # data style that is posted to export_view in template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }

        # Put 'group_selected_list' in request session. See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session['group_selected_list'] = [str(self.group.id)]
        session.save()
        response = self.client.post(reverse('export_view'), data)

        ##
        # Get file and make assertions
        ##
        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # TODO: use subdirectory separator
        self.assertTrue(
            any('Per_questionnaire/Step_1_QUESTIONNAIRE/' + self.survey.code +
                '_test-questionnaire_en.csv'
                in element for element in zipped_file.namelist()),
            'Per_questionnaire/Step_1_QUESTIONNAIRE/' + self.survey.code +
            '_test-questionnaire_en.csv not in: ' + str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Per_questionnaire/Step_2_QUESTIONNAIRE/' + self.survey.code +
                '_test-questionnaire_en.csv'
                in element for element in zipped_file.namelist()),
            'Per_questionnaire/Step_2_QUESTIONNAIRE/' + self.survey.code +
            '_test-questionnaire_en.csv not in: ' + str(zipped_file.namelist())
        )

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content(self):
        """
        Without reuse
        """
        ##
        # Create component (step) QUESTIONNAIRE
        ##
        # create other component (step) QUESTIONNAIRE in same experimental
        # protocol
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'sid': self.survey.id}
        )
        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, questionnaire
        )
        dct = ObjectsFactory.create_data_configuration_tree(
            component_config)

        # First participant
        # Create patient/subject/subject_of_group
        # create other subject of group
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = Subject.objects.create(patient=patient)
        subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=self.group
        )
        self.group.subjectofgroup_set.add(subject_of_group)

        # Add response to questionnaire in NES and LimeSurvey

        # add response to limesurvey survey and the references in our db
        result = UtilTests().create_survey_participant(self.survey)
        # TODO:
        # acho que não precisa criar resposta do participante enquanto
        # estamos testando resposta para experimento.
        UtilTests().create_response_survey_mock(
            self.user, patient, self.survey, result['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject.id,
            response_table_columns['firstQuestion']: 'Al mondo!',
            response_table_columns['secondQuestion']: 'Til verden!'
        }
        self.lime_survey.add_response(self.sid, response_data)
        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/
        # 113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result['tid'],
            {'completed': datetime.utcnow().strftime('%Y-%m-%d')}
        )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=result['tid'],
            subject_of_group=subject_of_group
        )
        # End first participant

        # Second participant

        # Create patient/subject/subject_of_group

        # create other subject of group
        patient2 = UtilTests().create_patient_mock(changed_by=self.user)
        subject2 = Subject.objects.create(patient=patient2)
        subject_of_group2 = SubjectOfGroup.objects.create(
            subject=subject2, group=self.group
        )
        self.group.subjectofgroup_set.add(subject_of_group2)

        # Add response to questionnaire in NES and LimeSurvey
        # add response to limesurvey survey and the references in our db
        result = UtilTests().create_survey_participant(self.survey)
        # TODO:
        # acho que não precisa criar resposta do participante enquanto
        # estamos testando resposta para experimento.
        UtilTests().create_response_survey_mock(
            self.user, patient2, self.survey, result['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject2.id,
            response_table_columns['firstQuestion']: 'Ola mundo!',
            response_table_columns['secondQuestion']: 'Halló heimur!'
        }
        self.lime_survey.add_response(self.sid, response_data)
        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/
        # 113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result['tid'],
            {'completed': datetime.utcnow().strftime('%Y-%m-%d')}
        )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=result['tid'],
            subject_of_group=subject_of_group2
        )
        # End second participant

        # Post data to view
        # data style that is posted to export_view in template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) + '*Test '
                                                                  'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }

        # Put 'group_selected_list' in request session. See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session['group_selected_list'] = [str(self.group.id)]
        session.save()
        response = self.client.post(reverse('export_view'), data)

        # Extract zip file and make assertions
        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        zipped_file.extract(
            'NES_EXPORT/Experiment_data/Group_' +
            self.group.title.lower() +
            '/Per_questionnaire/Step_2_QUESTIONNAIRE/' +
            self.survey.code + '_test-questionnaire_en.csv', '/tmp'
        )

        with open(
                '/tmp/NES_EXPORT/Experiment_data/Group_' +
                self.group.title.lower() +
                '/Per_questionnaire/Step_2_QUESTIONNAIRE/' +
                self.survey.code + '_test-questionnaire_en.csv'
        ) as file:
            self.assertEqual(len(file.readlines()), 3)

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content_2(self):
        """
        With reuse
        """
        # by now: simple testing in browser is working (but make this test!)
        pass

    def test_two_groups_with_questionnaire_step_in_both_returns_correct_directory_structure(self):

        # create other group/experimental protocol
        root_component_2 = ObjectsFactory.create_block(self.experiment)
        group_2 = ObjectsFactory.create_group(
            self.experiment, root_component_2
        )

        # create subject of group
        patient_2 = UtilTests().create_patient_mock(changed_by=self.user)
        subject_2 = Subject.objects.create(patient=patient_2)
        subject_of_group_2 = SubjectOfGroup.objects.create(
            subject=subject_2, group=group_2
        )
        group_2.subjectofgroup_set.add(subject_of_group_2)

        # create questionnaire component (reuse Survey created in setUp)
        questionnaire_2 = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'sid': self.survey.id}
        )

        # include questionnaire in experimental protocol
        component_config_2 = ObjectsFactory.create_component_configuration(
            root_component_2, questionnaire_2
        )
        dct_2 = \
            ObjectsFactory.create_data_configuration_tree(component_config_2)

        # add response to limesurvey survey and the references in our db
        result_2 = UtilTests().create_survey_participant(self.survey)
        UtilTests().create_response_survey_mock(
            self.user, patient_2, self.survey, result_2['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result_2['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject_2.id,
            response_table_columns['firstQuestion']: 'Olá Mundo!',
            response_table_columns['secondQuestion']: 'Hallo Welt!'
        }
        self.lime_survey.add_response(self.sid, response_data)

        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result_2['tid'],
            {'completed': datetime.utcnow().strftime('%Y-%m-%d')}
        )
        ObjectsFactory.create_questionnaire_response(
            dct=dct_2,
            responsible=self.user, token_id=result_2['tid'],
            subject_of_group=subject_of_group_2
        )

        ##
        # Post data to view
        ##
        # data style that is posted to export_view in template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion',

                '1*' + str(group_2.id) + '*' + str(self.sid) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group_2.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group_2.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }

        # Put 'group_selected_list' in request session. See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session['group_selected_list'] = [str(self.group.id), str(group_2.id)]
        session.save()
        response = self.client.post(reverse('export_view'), data)

        ##
        # Get file and make assertions
        ##
        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # TODO: use subdirectory separator
        # assertions for first group
        self.assertTrue(
            any('Group_' + self.group.title + '/Experimental_protocol/' in
                element for element in zipped_file.namelist()),
            'Group_' + self.group.title + '/Experimental_Protocol/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + self.group.title + '/Per_participant/' in
                element for element in zipped_file.namelist()),
            'Group_' + self.group.title + '/Per_participant/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + self.group.title + '/Per_questionnaire/' in
                element for element in zipped_file.namelist()),
            'Group_' + self.group.title + '/Per_questionnaire/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + self.group.title + '/Questionnaire_metadata/' in
                element for element in zipped_file.namelist()),
            'Group_' + self.group.title + '/Questionnaire_metadata/ not in:' +
            str(zipped_file.namelist())
        )

        # assertions for second group
        self.assertTrue(
            any('Group_' + group_2.title + '/Experimental_protocol/' in
                element for element in zipped_file.namelist()),
            'Group_' + group_2.title + '/Experimental_Protocol/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + group_2.title + '/Per_participant/' in
                element for element in zipped_file.namelist()),
            'Group_' + group_2.title + '/Per_participant/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + group_2.title + '/Per_questionnaire/' in
                element for element in zipped_file.namelist()),
            'Group_' + group_2.title + '/Per_questionnaire/ not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any('Group_' + group_2.title + '/Questionnaire_metadata/' in
                element for element in zipped_file.namelist()),
            'Group_' + group_2.title + '/Questionnaire_metadata/ not in:' +
            str(zipped_file.namelist())
        )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_generic_data_colletion(self):

        # create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        ObjectsFactory.create_generic_data_colletion_file(gdc_data)

        ##
        # Post data to view
        ##
        # data style that is posted to export_view in template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'patient_selected': ['age*age'],
            'per_generic_data': ['on'],
            'headings': ['code'],
            'from[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*secondQuestion*secondQuestion',
                '1*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*acquisitiondate*acquisitiondate',
                '1*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*firstQuestion*firstQuestion',
                '1*' + str(self.group.id) + '*' + str(self.sid) +
                '*First Survey*secondQuestion*secondQuestion'
            ],
            'responses': ['short']
        }

        # Put 'group_selected_list' in request session. See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session['group_selected_list'] = [str(self.group.id)]
        session.save()
        response = self.client.post(reverse('export_view'), data)

        ##
        # Get file and make assertions
        ##
        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # TODO: use subdirectory separator
        self.assertTrue(
            any('Per_participant/Step_5_Generic_data_collection/'
                in element for element in zipped_file.namelist()),
            'Per_questionnaire/Step_5_Generic_data_collection/ not in: ' +
            str(zipped_file.namelist())
        )

        shutil.rmtree(self.TEMP_MEDIA_ROOT)
