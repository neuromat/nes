import os
import io
import tempfile
import zipfile
from datetime import datetime

import shutil
from unittest import skip

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from custom_user.tests_helper import create_user
from experiment.models import Component, Subject, SubjectOfGroup
from experiment.tests_original import ObjectsFactory
from patient.tests import UtilTests
from qdc import settings
from survey.abc_search_engine import Questionnaires
from survey.tests_helper import create_survey


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

    @staticmethod
    def create_limesurvey_questionnaire(lime_survey):
        # create questionnaire at LiveSurvey
        survey_title = 'Test questionnaire'
        sid = lime_survey.add_survey(999999, survey_title, 'en', 'G')

        # create required group/questions for LimeSurvey/NES integration
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests',
                'NESIdentification_group.lsg'
        )) as file:
            content = file.read()
            lime_survey.insert_questions(sid, content, 'lsg')

        # create other group of questions/questions for the tests
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests',
                'limesurvey_group_2.lsg'
        )) as file:
            content = file.read()
            lime_survey.insert_questions(sid, content, 'lsg')

        # activate survey and tokens
        lime_survey.activate_survey(sid)
        lime_survey.activate_tokens(sid)

        return sid

    def create_nes_questionnaire(self, root_component):
        """
        Create questionnaire component in experimental protocol and return
        data configuration tree associated to that questionnaire component
        :return: DataConfigurationTree model instance
        """
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'sid': self.survey.id}
        )
        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            root_component, questionnaire
        )
        return ObjectsFactory.create_data_configuration_tree(component_config)

    def add_responses_to_limesurvey_survey(self, subject_of_group, dct):
        result = UtilTests().create_survey_participant(self.survey)
        # TODO:
        # acho que não precisa criar resposta do participante enquanto
        # estamos testando resposta para experimento.
        UtilTests().create_response_survey_mock(
            self.user, subject_of_group.subject.patient, self.survey,
            result['tid']
        )
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject_of_group.subject.id,
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
            subject_of_group=subject_of_group
        )

    def create_subject_of_group(self, group):
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = Subject.objects.create(patient=patient)
        subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=group
        )
        self.group.subjectofgroup_set.add(subject_of_group)

        return subject_of_group

    def append_group_session_variable(self, variable, group_ids):
        """
        See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        # for the form that it is done

        :param variable: variable to be appended to session
        :param group_ids: list of group ids (strins) as the value of the
        session variable
        """
        session = self.client.session
        session[variable] = group_ids
        session.save()

    def get_zipped_file(self, response):
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        return zipped_file

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        self.user = create_user(Group.objects.all())
        self.client.login(username=self.user.username, password='passwd')

        # create experiment/experimental protocol/group
        self.experiment = ObjectsFactory.create_experiment(
            ObjectsFactory.create_research_project(self.user)
        )
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create patient/subject/subject_of_group
        self.subject_of_group = self.create_subject_of_group(self.group)

        self.lime_survey = Questionnaires()
        self.sid = self.create_limesurvey_questionnaire(self.lime_survey)

        # create questionnaire in NES
        self.survey = create_survey(self.sid)
        dct = self.create_nes_questionnaire(self.root_component)

        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            self.subject_of_group, dct
        )

    def tearDown(self):
        self.lime_survey.delete_survey(self.sid)
        self.client.logout()

    def test_same_questionnaire_used_in_different_steps_return_correct_zipfile_content(self):
        # TODO: testar com sobreposição do subdiretório media

        # Create other component (step) QUESTIONNAIRE in same experimental
        # protocol, from LimeSurvey survey created in setUp
        dct = self.create_nes_questionnaire(self.root_component)

        # Create one more patient/subject/subject_of_group besides those of
        # setUp
        subject_of_group = self.create_subject_of_group(self.group)

        self.add_responses_to_limesurvey_survey(subject_of_group, dct)

        # Put 'group_selected_list' in request session.
        self.append_group_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
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
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        zipped_file = self.get_zipped_file(response)

        self.assertTrue(
            any(os.path.join(
                'Per_questionnaire',
                'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_questionnaire',
                'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) +
            'not in: ' + str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) +
            'not in: ' + str(zipped_file.namelist())
        )

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content(self):
        """
        Without reuse
        """
        # create questionnaire in NES
        dct = self.create_nes_questionnaire(self.root_component)

        # Create first patient/subject/subject_of_group besides those of
        # setUp
        subject_of_group = self.create_subject_of_group(self.group)
        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group, dct
        )

        # Create second patient/subject/subject_of_group
        subject_of_group2 = self.create_subject_of_group(self.group)
        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group2, dct
        )

        # Put 'group_selected_list' in request session.
        self.append_group_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ),
            '/tmp'
        )

        with open(
            os.path.join(
                os.sep, 'tmp',
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            )

        ) as file:
            self.assertEqual(len(file.readlines()), 3)

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content_2(self):
        """
        With reuse
        """
        # by now: simple testing in browser is working (but, make this test ;)
        pass

    def test_two_groups_with_questionnaire_step_in_both_returns_correct_directory_structure(self):

        # create other group/experimental protocol
        root_component2 = ObjectsFactory.create_block(self.experiment)
        group2 = ObjectsFactory.create_group(self.experiment, root_component2)

        # create patient/subject/subject_of_group
        subject_of_group2 = self.create_subject_of_group(group2)

        # create questionnaire component (reuse Survey created in setUp)
        dct2 = self.create_nes_questionnaire(root_component2)

        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group2, dct2
        )

        # Put 'group_selected_list' in request session.
        self.append_group_session_variable(
            'group_selected_list', [str(self.group.id), str(group2.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
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

                '1*' + str(group2.id) + '*' + str(self.sid) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        zipped_file = self.get_zipped_file(response)

        # assertions for first group
        self.assertTrue(
            any(os.path.join(
                'Group_' + self.group.title, 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + self.group.title, 'Experimental_Protocol'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + self.group.title, 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + self.group.title, 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + self.group.title, 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + self.group.title, 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + self.group.title, 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + self.group.title, 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

        # assertions for second group
        self.assertTrue(
            any(os.path.join(
                'Group_' + group2.title, 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + group2.title, 'Experimental_Protocol'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + group2.title, 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + group2.title, 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + group2.title, 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + group2.title, 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + group2.title, 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + group2.title, 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

    @skip  # this test is in progress
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
