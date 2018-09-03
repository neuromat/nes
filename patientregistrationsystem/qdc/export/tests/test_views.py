import csv
import os
import io
import tempfile
import zipfile
from datetime import datetime

import shutil

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test import override_settings

from experiment.models import Component, ComponentConfiguration
from experiment.tests_original import ObjectsFactory
from export.export_utils import create_list_of_trees
from export.tests.tests_helper import ExportTestCase
from patient.tests import UtilTests
from qdc import settings
from survey.abc_search_engine import Questionnaires
from survey.tests_helper import create_survey


class ExportQuestionnaireTest(ExportTestCase):

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
        """Create questionnaire component in experimental protocol and return
        data configuration tree associated to that questionnaire component
        :param root_component: Block(Component) model instance
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

    def setUp(self):
        super(ExportQuestionnaireTest, self).setUp()

        self.lime_survey = Questionnaires()
        self.sid = self.create_limesurvey_questionnaire(self.lime_survey)

        # create questionnaire in NES
        self.survey = create_survey(self.sid)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            self.subject_of_group, self.data_configuration_tree
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
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        self.add_responses_to_limesurvey_survey(subject_of_group, dct)

        self.append_session_variable(
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
        dct = self.create_nes_questionnaire(self.root_component)  # TODO: já
        #  criado no setUP

        # Create first patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)
        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group, dct
        )

        # Create second patient/subject/subject_of_group
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = \
            ObjectsFactory.create_subject_of_group(self.group, subject)
        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group2, dct
        )

        self.append_session_variable(
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

        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ),
            '/tmp'  # TODO: 1) use os.sep; 2) use tempfile
        )

        with open(
            os.path.join(
                os.sep, 'tmp',  # TODO: use tempfile
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            )
        ) as file:
            # there's 3 lines, header line + 2 responses lines
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
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = \
            ObjectsFactory.create_subject_of_group(group2, subject)

        # create questionnaire component (reuse Survey created in setUp)
        dct2 = self.create_nes_questionnaire(root_component2)

        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group2, dct2
        )

        self.append_session_variable(
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

        zipped_file = self.get_zipped_file(response)

        # assertions for first group
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Experimental_Protocol'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

        # assertions for second group
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Experimental_Protocol'
            ) +
            ' not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

    def test_export_with_abbreviated_question_text(self):
        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
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

        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ),
            '/tmp'  # TODO: 1) use os.sep; 2) use tempfile
        )

        with open(
                os.path.join(
                    os.sep, 'tmp',  # TODO: use tempfile
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
                )
        ) as file:
            csv_line1 = next(csv.reader(file))
            self.assertEqual(len(csv_line1), 5)

    def test_reusing_experimental_protocol_in_two_groups_returns_correct_directory_structure(self):

        # create other group and associate the same experimental protocol
        group2 = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create patient/subject/subject_of_group
        patient2 = UtilTests().create_patient_mock(changed_by=self.user)
        subject2 = ObjectsFactory.create_subject(patient2)
        subject_of_group2 = \
            ObjectsFactory.create_subject_of_group(group2, subject2)

        # add response to limesurvey survey and the references in our db
        self.add_responses_to_limesurvey_survey(
            subject_of_group2, self.data_configuration_tree
        )

        self.append_session_variable(
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
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion',

                '1*' + str(group2.id) + '*' + str(self.sid) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # assertions for first group
        self.assertFalse(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant',
                'Participant_' + patient2.code
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant',
                'Participant_' + patient2.code
            ) + ' is in: ' + str(zipped_file.namelist())
        )
        self.assertFalse(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant',
                'Participant_' + self.patient.code
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant',
                'Participant_' + self.patient.code
            ) + ' is in: ' + str(zipped_file.namelist())
        )


class ExportDataCollectionTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(ExportDataCollectionTest, self).setUp()

    def tearDown(self):
        self.client.logout()
        shutil.rmtree(self.TEMP_MEDIA_ROOT)

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

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "generic_data_collection"):
            generic_component_configuration = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assertTrue(
                any(os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                )
                    in element for element in zipped_file.namelist()),
                os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                ) + ' not in: ' + str(zipped_file.namelist())
            )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_digital_game_phase_data_colletion(self):
        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree}
        )

        # include dgp component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, dgp
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' digital game data file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(
            dct, self.subject_of_group
        )

        ObjectsFactory.create_digital_game_phase_file(dgp_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_goalkeeper_game_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "digital_game_phase"):
            digital_game_phase_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = digital_game_phase_component_configuration.component
            step_number = path[-1][4]

            self.assertTrue(
                any(os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                )
                    in element for element in zipped_file.namelist()),
                os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                ) + ' not in: ' + str(zipped_file.namelist())
            )


class ExportParticipants(ExportTestCase):

    def setUp(self):
        super(ExportParticipants, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_export_participants_without_questionnaires_returns_zipped_file(self):
        """
        Test created when exporting participants, without questionnaires
        avulsely answered by them, gave yellow screen. See Jira Issue NES-864.
        """

        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        self.get_zipped_file(response)


class ExportSelection(ExportTestCase):

    def tearDown(self):
        self.client.logout()

    def test_expire_section_when_in_last_export_form_returns_to_first_export_page(self):
        """ Path that is followed when the session is expired and it tries
        to generates the zipped file after loggin again
        1. Flush the session
        2. Post data to export view: the response contains the url to
        reverse to login page
        3. Post credentials in login page to login
        4. Get the reversed url that has to point at export's first page
        """

        self.client.session.flush()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        response2 = self.client.post(response.url, {
            'username': self.user.username,
            'password': self.user_passwd
        })

        # when session expires the request is made with get
        response3 = self.client.get(response2.url)

        # TODO:
        # see if it's possible to get 'http://testserver' without hardcode
        self.assertEqual(
            response3.url, 'http://testserver' + reverse('export_menu')
        )


class ExportEegTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(ExportEegTest, self).setUp()

    def tearDown(self):
        self.client.logout()
        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_eeg(self):
        # create eeg component
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )

        # include eeg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' eeg file
        eegdata = ObjectsFactory.create_eeg_data_collection_data(
            dct, self.subject_of_group, eeg_set
        )
        ObjectsFactory.create_eeg_data_collection_file(eegdata)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        # self.append_group_session_variable(
        #     'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_eeg_raw_data ': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "eeg"):
            eeg_conf = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = eeg_conf.component
            step_number = path[-1][4]

            lst = os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper())

            self.assertTrue(
                any(os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                )
                    in element for element in zipped_file.namelist()),
                os.path.join(
                    'Per_participant', 'Participant_' + self.patient.code,
                    'Step_' + str(step_number) + '_' +
                    component_step.component_type.upper()
                ) + ' not in: ' + str(zipped_file.namelist())
            )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_emg(self):
        # create emg component
        self.manufacturer = ObjectsFactory.create_manufacturer()
        self.software = ObjectsFactory.create_software(self.manufacturer)
        self.software_version = ObjectsFactory.create_software_version(
            self.software)
        self.tag_emg = ObjectsFactory.create_tag('EMG')
        emg_set = ObjectsFactory.create_emg_setting(self.experiment,
                                                    self.software_version)
        emg_comp = ObjectsFactory.create_component(self.experiment,
                                                   Component.EMG,
                                                   kwargs={'emg_set': emg_set}
        )

        # include emg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, emg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' emg file
        emgdata = ObjectsFactory.create_emg_data_collection_data(
            dct, self.subject_of_group, emg_set
        )
        ObjectsFactory.create_emg_data_collection_file(emgdata)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        # self.append_group_session_variable(
        #     'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_emg_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "emg"):
            emg_conf = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = emg_conf.component
            step_number = path[-1][4]

            lst = os.path.join('Per_participant',
                               'Participant_' +
                               self.patient.code,
                               'Step_' + str(step_number) + '_' +
                               component_step.component_type.upper())

            self.assertTrue(
                any(os.path.join(lst) in element for element in
                    zipped_file.namelist()),
                    lst + ' not in: ' + str(zipped_file.namelist())
            )

    # @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    # def test_export_experiment_with_stimulus(self):
    #     # create stimulus component
    #     stimulus_type = StimulusType.objects.create(name="Auditivo")
    #     stimulus_set = Stimulus.objects.create(identification="Stimulus "
    #                                                   "identification",
    #                                            stimulus_type=stimulus_type
    #     )
    #
    #     stimulus_comp = ObjectsFactory.create_component(self.experiment,
    #                                                Component.STIMULUS,
    #                                                kwargs={'stimulus_set': stimulus_set}
    #     )
    #
    #     # include emg component in experimental protocol
    #     component_config = ObjectsFactory.create_component_configuration(
    #         self.root_component, stimulus_comp
    #     )
    #     dct = ObjectsFactory.create_data_configuration_tree(component_config)
    #
    #     # 'upload' stimulus file
    #     stimulusdata = ObjectsFactory.create_stimulus_data_collection_data(
    #         dct, self.subject_of_group, stimulus_set
    #     )
    #     ObjectsFactory.create_stimulus_data_collection_file(stimulusdata)
    #
    #     self.append_group_session_variable(
    #         'group_selected_list', [str(self.group.id)]
    #     )
    #
    #     # Post data to view: data style that is posted to export_view in
    #     # template
    #     data = {
    #         'per_questionnaire': ['on'],
    #         'per_participant': ['on'],
    #         'per_generic_data': ['on'],
    #         'headings': ['code'],
    #         'patient_selected': ['age*age'],
    #         'action': ['run'],
    #         'responses': ['short']
    #     }
    #     response = self.client.post(reverse('export_view'), data)
    #
    #     # get the zipped file to test against its content
    #     file = io.BytesIO(response.content)
    #     zipped_file = zipfile.ZipFile(file, 'r')
    #     self.assertIsNone(zipped_file.testzip())
    #
    #     for path in create_list_of_trees(self.group.experimental_protocol,
    #                                      "stimulus"):
    #         stimulus_conf = \
    #             ComponentConfiguration.objects.get(pk=path[-1][0])
    #         component_step = stimulus_conf.component
    #         step_number = path[-1][4]
    #
    #         lst = os.path.join('Per_participant',
    #                            'Participant_' +
    #                            self.patient.code,
    #                            'Step_' + str(step_number) + '_' +
    #                            component_step.component_type.upper())
    #
    #         self.assertTrue(
    #             any(os.path.join(lst) in element for element in
    #                 zipped_file.namelist()),
    #                 lst + ' not in: ' + str(zipped_file.namelist())
    #         )
    #
