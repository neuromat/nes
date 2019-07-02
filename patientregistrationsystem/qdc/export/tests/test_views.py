import csv
import os
import io
import tempfile
import zipfile
from datetime import date

import shutil
from unittest.mock import patch

from django.core.files import File
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.test import override_settings

from experiment.models import Component, ComponentConfiguration, \
    ComponentAdditionalFile, BrainAreaSystem, BrainArea,\
    TMSLocalizationSystem, HotSpot, TMSData, \
    CoilOrientation, DirectionOfTheInducedCurrent
from experiment.tests.tests_original import ObjectsFactory
from export.export_utils import create_list_of_trees
from export.tests.mocks import set_mocks1, LIMESURVEY_SURVEY_ID, set_mocks2, set_mocks3, set_mocks4, \
    set_mocks5
from export.tests.tests_helper import ExportTestCase
from patient.tests.tests_orig import UtilTests
from survey.tests.tests_helper import create_survey

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


class ExportQuestionnaireTest(ExportTestCase):

    def setUp(self):
        super(ExportQuestionnaireTest, self).setUp()

        # Create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(LIMESURVEY_SURVEY_ID)
        self.data_configuration_tree = self.create_nes_questionnaire(self.root_component)

        # Add response's participant to limesurvey survey and the references
        # in our db
        self.questionnaire_response = ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group)

    def tearDown(self):
        self.client.logout()

    def create_nes_questionnaire(self, root_component):
        """Create questionnaire component in experimental protocol and return
        data configuration tree associated to that questionnaire component
        :param root_component: Block(Component) model instance
        :return: DataConfigurationTree model instance
        """
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': self.survey}
        )
        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            root_component, questionnaire
        )
        return ObjectsFactory.create_data_configuration_tree(component_config)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content(self, mockServer):
        """Without reuse"""

        set_mocks1(mockServer)

        # Create questionnaire in NES
        dct = self.create_nes_questionnaire(self.root_component)  # TODO: já criado no setUP

        # Create first patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group
        )

        # Create second patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=3,
            subject_of_group=subject_of_group2)
        self.append_session_variable('group_selected_list', [str(self.group.id)])

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), temp_dir
        )

        with open(
            os.path.join(
                temp_dir,
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            )
        ) as file:
            # There're 3 lines, header line + 2 responses lines
            self.assertEqual(len(file.readlines()), 3)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_same_questionnaire_used_in_different_steps_return_correct_zipfile_content(self, mockServer):
        set_mocks2(mockServer)

        # Create other component (step) QUESTIONNAIRE in same experimental
        # protocol, from LimeSurvey survey created in setUp
        # TODO: see if it's correct before commit. It's creating other questionnaire
        dct = self.create_nes_questionnaire(self.root_component)

        # Create one more patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group
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
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
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
        self.assertTrue(any(os.path.join(
            'Per_questionnaire', 'Step_2_QUESTIONNAIRE', self.survey.code + '_test-questionnaire_en.csv')
                            in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) +
            'not in: ' + str(zipped_file.namelist())
        )

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content_2(self):
        """
        With reuse
        """
        # by now: simple testing in browser is working (but, make this test ;)
        pass

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_two_groups_with_questionnaire_step_in_both_returns_correct_directory_structure(self, mockServer):
        set_mocks3(mockServer)

        # Create other group/experimental protocol
        root_component2 = ObjectsFactory.create_block(self.experiment)
        group2 = ObjectsFactory.create_group(self.experiment, root_component2)

        # Create questionnaire component (reuse Survey created in setUp)
        dct2 = self.create_nes_questionnaire(root_component2)

        # Create patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct2,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group2
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
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
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

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_with_abbreviated_question_text(self, mockServer):
        set_mocks4(mockServer)

        self.append_session_variable('group_selected_list', [str(self.group.id)])

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), temp_dir
        )

        with open(
                os.path.join(
                    temp_dir,
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
                )
        ) as file:
            csv_line1 = next(csv.reader(file))
            self.assertEqual(len(csv_line1), 6)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_reusing_experimental_protocol_in_two_groups_returns_correct_directory_structure(self, mockServer):
        set_mocks3(mockServer)

        # Create other group and associate the same experimental protocol
        group2 = ObjectsFactory.create_group(self.experiment, self.root_component)

        # Create patient/subject/subject_of_group
        patient2 = UtilTests().create_patient(changed_by=self.user)
        subject2 = ObjectsFactory.create_subject(patient2)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject2)

        ObjectsFactory.create_questionnaire_response(
            dct=self.data_configuration_tree,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group2
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
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # Assertions for first group
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

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_participant_age_in_responses_is_age_when_questionnaire_was_filled_1(self, mockServer):
        """Test over experiment questionnaire response"""

        set_mocks4(mockServer)

        self.append_session_variable('group_selected_list', [str(self.group.id)])

        # Change questionnaire respose date for testing
        self.questionnaire_response.date = date(2016, 7, 7)
        self.questionnaire_response.save()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'per_questionnaire': ['on'],
            'action': ['run'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir,
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1],
                ExportParticipants.subject_age(
                    self.patient.date_birth, self.questionnaire_response)
            )

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_participant_age_in_responses_is_age_when_questionnaire_was_filled_2(self, mockServer):
        """Test over participant questionnaire responses"""

        set_mocks5(mockServer)

        # In setUp we created experiment questionnaire response. Here we
        # create a participant questionnaire response (entrance questionnaire)
        questionnaire_response = UtilTests.create_response_survey(
            responsible=self.user, patient=self.patient, survey=self.survey)
        # change questionnaire respose date for testing
        questionnaire_response.date = date(2016, 4, 17)
        questionnaire_response.save()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'per_questionnaire': ['on'],
            'action': ['run'],
            'headings': ['code'],
            'to[]': [
                '0*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join('NES_EXPORT', 'Participants.csv'), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1],
                self.subject_age(
                    self.patient.date_birth, self.questionnaire_response
                )
            )

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_create_csv_file(self, mockServer):
        set_mocks4(mockServer)

        self.append_session_variable('group_selected_list', [str(self.group.id)])

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
            'filesformat': ['csv']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ),
            temp_dir
        )

        with open(
                os.path.join(
                    temp_dir,
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
                )
        ) as file:
            dialect = csv.Sniffer().sniff(file.readline(), [',', '\t'])
            file.seek(0)
            self.assertEqual(dialect.delimiter, ",")

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_create_tsv_file(self, mockServer):
        set_mocks4(mockServer)

        self.append_session_variable('group_selected_list', [str(self.group.id)])

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
            'filesformat': ['tsv']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.tsv'
            ),
            temp_dir
        )

        with open(
                os.path.join(
                    temp_dir,
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.tsv'
                )
        ) as file:
            dialect = csv.Sniffer().sniff(file.readline(), [',', '\t'])
            file.seek(0)
            self.assertEqual(dialect.delimiter, "\t")

        shutil.rmtree(temp_dir)


class ExportDataCollectionTest(ExportTestCase):

    def setUp(self):
        super(ExportDataCollectionTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_generic_data_colletion(self):
        # Create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(
            self.group.experimental_protocol, "generic_data_collection"
        )[0]

        generic_component_configuration = \
            ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = generic_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'Generic_Data_Collection_1',
            os.path.basename(gdcf.file.name), zipped_file
        )
        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1',
            os.path.basename(adf.file.name), zipped_file
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

        dgpf = ObjectsFactory.create_digital_game_phase_file(dgp_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_goalkeeper_game_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the digital_game_phase step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "digital_game_phase")[0]

        digital_game_phase_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = digital_game_phase_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(step_number, component_step,
                                                     'DigitalGamePhaseData_1',
                                                     os.path.basename(dgpf.file.name),
                                                     zipped_file)
        self.assert_per_participant_step_file_exists(step_number, component_step,
                                                     'AdditionalData_1',
                                                     os.path.basename(adf.file.name),
                                                     zipped_file)

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
        eegdata = ObjectsFactory.create_eeg_data(
            dct, self.subject_of_group, eeg_set
        )

        eegf = ObjectsFactory.create_eeg_file(eegdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_eeg_raw_data ': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "eeg")[0]
        eeg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = eeg_conf.component
        step_number = path[-1][4]
        self.assert_per_participant_step_file_exists(step_number, component_step, 'EEGData_1',
                                                     os.path.basename(eegf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(step_number, component_step, 'AdditionalData_1',
                                                     os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_emg(self):
        # Create emg component
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

        emgf = ObjectsFactory.create_emg_data_collection_file(emgdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_emg_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "emg")[0]
        emg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = emg_conf.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(step_number, component_step, 'EMGData_1',
                                                     os.path.basename(emgf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(step_number, component_step, 'AdditionalData_1',
                                                     os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_tms(self):
        # Create tms component
        tms_set = ObjectsFactory.create_tms_setting(self.experiment)

        tms_comp = ObjectsFactory.create_component(
            self.experiment, Component.TMS,
            kwargs={'tms_set': tms_set}
        )

        # Include tms component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, tms_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        doic = DirectionOfTheInducedCurrent.objects.create(
            name="Direction of Induced Current"
        )

        coilor = CoilOrientation.objects.create(
            name="Coil Orientation"
        )

        tmsdataaux = TMSData.objects.create(
            tms_setting=tms_set,
            data_configuration_tree=dct,
            subject_of_group=self.subject_of_group,
            coil_orientation=coilor,
            description="Teste TMS",
            direction_of_induced_current=doic
        )

        brainareasystem = BrainAreaSystem.objects.create(name='Lobo frontal')

        brainarea = BrainArea.objects.create(name='Lobo frontal',
                                             brain_area_system=brainareasystem)

        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, 'image.bin'), 'wb') as f:
            f.write(b'carambola')
        temp_file = f.name

        tms_local_sys = TMSLocalizationSystem.objects.create(
            name="TMS name", brain_area=brainarea,
            tms_localization_system_image=temp_file
        )

        hotspot = HotSpot.objects.create(
            tms_data=tmsdataaux,
            name="TMS Data Collection File",
            tms_localization_system=tms_local_sys
        )

        ObjectsFactory.create_hotspot_data_collection_file(hotspot)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_tms_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "tms"):
            tms_conf = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = tms_conf.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         '',
                                                         'hotspot_map.png',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_generic_data_colletion_2_groups(self):
        # Create second group; create patient/subject/subject_of_group
        root_component1 = ObjectsFactory.create_block(self.experiment)
        group1 = ObjectsFactory.create_group(
            self.experiment, root_component1
        )
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = \
            ObjectsFactory.create_subject_of_group(group1, subject1)

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
        component_config1 = ObjectsFactory.create_component_configuration(
            root_component1, gdc
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdc_data1 = ObjectsFactory.create_generic_data_collection_data(
            dct1, subject_of_group1
        )

        ObjectsFactory.create_generic_data_collection_file(gdc_data)
        ObjectsFactory.create_generic_data_collection_file(gdc_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group1.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "generic_data_collection"):
            generic_component_configuration = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'Generic_Data_Collection_1',
                                                         'file.bin',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

        for path in create_list_of_trees(group1.experimental_protocol,
                                         "generic_data_collection"):
            generic_component_configuration = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'Generic_Data_Collection_1',
                                                         'file.bin',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_goalkeeper_game_data_2_groups(self):
        # Create second group; create patient/subject/subject_of_group
        root_component1 = ObjectsFactory.create_block(self.experiment)
        group1 = ObjectsFactory.create_group(
            self.experiment, root_component1
        )
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = \
            ObjectsFactory.create_subject_of_group(group1, subject1)

        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree}
        )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, dgp
        )
        component_config1 = ObjectsFactory.create_component_configuration(
            root_component1, dgp
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' data game phase collection file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(
            dct, self.subject_of_group
        )

        dgp_data1 = ObjectsFactory.create_digital_game_phase_data(
            dct1, subject_of_group1
        )

        ObjectsFactory.create_digital_game_phase_file(dgp_data)
        ObjectsFactory.create_digital_game_phase_file(dgp_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group1.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_goalkeeper_game_data': ['on'],
            # 'per_additional_data': ['on'],
            'headings': ['code'],
            'filesformat': ['csv'],
            'responses': ['short'],
            'patient_selected': ['age*age'],
            'action': ['run']
        }
        response = self.client.post(reverse('export_view'), data)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_step_additional_data(self):
        # Create generic data collection (gdc) component, it could've been any data collection
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # Create a file and add it as an additional file of the step
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'stepadditionaldata.bin'), 'wb') as f:
                f.write(b'carambola')

                with File(open(f.name, 'rb')) as file:
                    ComponentAdditionalFile.objects.create(component=gdc, file=file)

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
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

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "generic_data_collection")[0]
        generic_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = generic_component_configuration.component
        step_number = path[-1][4]

        self.assert_step_data_files_exists(step_number, component_step,
                                           'AdditionalData',
                                           os.path.basename(f.name),
                                           zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_stimulus_media_file(self):
        # Create a stimulus component
        stimulus_type = ObjectsFactory.create_stimulus_type()

        with tempfile.TemporaryDirectory() as tmpdirname:
            f = ObjectsFactory.create_binary_file(tmpdirname)

            with File(open(f.name, 'rb')) as file:
                stimulus = ObjectsFactory.create_component(
                    self.experiment, Component.STIMULUS,
                    kwargs={'stimulus_type': stimulus_type,
                            'media_file': file}
                )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, stimulus
        )

        dtc = ObjectsFactory.create_data_configuration_tree(component_config)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_stimulus_data': ['on'],
            'per_additional_data': ['on'],
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

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "stimulus")[0]
        stimulus_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = stimulus_component_configuration.component
        step_number = path[-1][4]

        self.assert_step_data_files_exists(step_number, component_step, '',
                                           os.path.basename(f.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_age_is_age_at_first_data_collection(self):
        """Create two data collections: generic data collection and eeg data-
        collection
        """
        # Generic data collection (gdc) stuff
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        # change generic data collection date for testing
        gdc_data.date = date(2018, 7, 7)
        gdc_data.save()
        ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # eeg data collection stuff
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        eeg_data = ObjectsFactory.create_eeg_data(
            dct, self.subject_of_group, eeg_set
        )
        # change eeg data collection date for testing
        eeg_data.date = date(2012, 5, 5)
        eeg_data.save()
        ObjectsFactory.create_eeg_file(eeg_data)

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

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT', 'Participant_data', 'Participants.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participant_data', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1], self.subject_age(self.patient.date_birth, eeg_data)
            )

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_age_is_age_today_if_no_data_collection(self):
        # Create eeg step
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )
        ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )

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

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT', 'Participant_data', 'Participants.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participant_data', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1], self.subject_age(self.patient.date_birth)
            )

        shutil.rmtree(temp_dir)


class ExportParticipants(ExportTestCase):

    def setUp(self):
        super(ExportParticipants, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_export_participants_without_questionnaires_returns_zipped_file(self):
        """Test created when exporting participants, without questionnaires
        avulsely answered by them, gave yellow screen. See Jira Issue NES-864.
        """
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        self.get_zipped_file(response)

    def test_export_participants_age_is_age_at_export_date_if_no_questionnaire_response(self):
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(os.path.join('NES_EXPORT', 'Participants.csv'), temp_dir)

        with open(os.path.join(temp_dir, 'NES_EXPORT', 'Participants.csv')) \
                as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(rows[1][1], self.subject_age(self.patient.date_birth))

        shutil.rmtree(temp_dir)

    def test_export_participants_does_not_select_any_attribute_returns_redirect_and_display_warning_message(self):
        response = self.client.post(reverse('export_view'), {'action': ['run']}, follow=True)
        # After POSTing without 'patient_selected' as key for data nargs, the
        # system first redirects to export/view, then to export/, so take
        # the first redirection url and status code.
        first_redirect_url, status_code = response.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(first_redirect_url, reverse('export_view'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, _('Please select at least one patient attribute'))


class ExportSelection(ExportTestCase):

    def setUp(self):
        super(ExportSelection, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_experiment_selection_selecting_group(self):
        data = {
            'id_research_projects': self.experiment.research_project.id,
            'id_experiments': self.experiment.id,
            'group_selected': self.group.id,
            'action': 'next-step-participants'
        }

        self.append_session_variable('id_research_projects', [str(self.experiment.research_project.id)])
        self.append_session_variable('id_experiments', [str(self.experiment.id)])
        self.append_session_variable('group_selected', [str(self.group.id)])

        response = self.client.post(reverse('experiment_selection'), data)

        self.assertRedirects(response, '/export/view/', status_code=302, target_status_code=200)

    def test_experiment_selection_withou_select_group(self):

        data = {
            'id_research_projects': self.experiment.research_project.id,
            'id_experiments': self.experiment.id,
            'action': 'next-step-participants'
        }

        self.append_session_variable('id_research_projects', [str(self.experiment.research_project.id)])
        self.append_session_variable('id_experiments', [str(self.experiment.id)])
        response = self.client.post(reverse('experiment_selection'), data)
        self.assertEqual(response.status_code, 200)

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
        self.assertRedirects(response3, reverse('export_menu'), status_code=302, target_status_code=200)


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT)
