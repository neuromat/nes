import csv
import os
import io
import re
import sys
import tempfile
import zipfile
from datetime import date, datetime

import shutil
from unittest.mock import patch

from django.core.files import File
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.test import override_settings
from goodtables import validate

from experiment.models import Component, ComponentConfiguration, \
    ComponentAdditionalFile, BrainAreaSystem, BrainArea, TMSLocalizationSystem, HotSpot, TMSData, \
    CoilOrientation, DirectionOfTheInducedCurrent, EEGFile, EMGFile, Stimulus, ContextTree, EEGData
from experiment.tests.tests_helper import ObjectsFactory
from export import input_export
from export.export import PROTOCOL_IMAGE_FILENAME, PROTOCOL_DESCRIPTION_FILENAME, EEG_DEFAULT_SETTING_FILENAME, \
    EEG_SETTING_FILENAME, TMS_DATA_FILENAME, HOTSPOT_MAP, EMG_SETTING_FILENAME, EMG_DEFAULT_SETTING, \
    TMS_DEFAULT_SETTING_FILENAME, CONTEXT_TREE_DEFAULT, ExportExecution
from export.export_utils import create_list_of_trees
from export.models import Export
from export.tests.mocks import set_mocks1, LIMESURVEY_SURVEY_ID_1, set_mocks2, set_mocks3, set_mocks4, \
    set_mocks5, set_mocks6, set_mocks7, update_mocks4_full_and_abbreviated, update_mocks7_full, \
    update_mocks7_abbreviated, \
    LIMESURVEY_SURVEY_ID_2, set_mocks8, update_mocks10_full, update_mocks10_abbreviated, set_mocks9, set_mocks10, \
    set_mocks11, \
    update_mocks11_full, update_mocks11_abbreviated, update_mocks6_full, update_mocks6_abbreviated, update_mocks9_full, \
    update_mocks9_abbreviated
from export.tests.tests_helper import ExportTestCase
from export.views import EXPORT_DIRECTORY, abbreviated_data, PATIENT_FIELDS, DIAGNOSIS_FIELDS
from patient.tests.tests_orig import UtilTests
from survey.tests.tests_helper import create_survey
from survey.survey_utils import HEADER_EXPLANATION_FIELDS

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


class ExportQuestionnaireTest(ExportTestCase):

    def setUp(self):
        super(ExportQuestionnaireTest, self).setUp()

        # Create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        self.data_configuration_tree = self._create_nes_questionnaire(self.root_component)

        # Add response's participant to limesurvey survey and the references
        # in our db
        self.questionnaire_response = ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree, responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group)

    def tearDown(self):
        self.client.logout()

    def _create_nes_questionnaire(self, root_component):
        """Create questionnaire component in experimental protocol and return
        data configuration tree associated to that questionnaire component
        :param root_component: Block(Component) model instance
        :return: DataConfigurationTree model instance
        """
        self.questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': self.survey})
        # Include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            root_component, self.questionnaire)

        return ObjectsFactory.create_data_configuration_tree(component_config)

    def _create_questionnaire_export_data(self):
        # Create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        self.questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': self.survey})
        # Include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, self.questionnaire)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # Add response's participant to limesurvey survey and the references
        # in our db
        ObjectsFactory.create_questionnaire_response(
            dct=dct, responsible=self.user, token_id=1, subject_of_group=self.subject_of_group)
    
    @staticmethod
    def _set_all_questions():
        return [
            ({'code': 'acquisitiondate', 'full': _('Acquisition date:'), 'abbreviated': _('Acquisition date:')},
             'D', 'datetime', '%Y-%m-%d %H:%M:%S'),
            ({'code': 'funfpunktewahl', 'full': _('Fünf Punkte Wahl'), 'abbreviated': _('Fünf Punkte Wahl')},
             '5', 'string', 'default'),
            ({'code': 'dropdownliste', 'full': _('Dropdown Liste'), 'abbreviated': _('Dropdown Liste')},
             '!', 'string', 'default'),
            ({'code': 'listeradio', 'full': _('Liste (radio)'), 'abbreviated': _('Liste (radio)')},
             'L', 'string', 'default'),
            ({'code': 'listemitkommentar', 'full': _('Liste mit Kommentar'), 'abbreviated': _('Liste mit Komme..')},
             'O', 'string', 'default'),
            ({'code': 'listemitkommentar[comment]', 'full': _('Liste mit Kommentar [Comment]'), 'abbreviated': _('Liste mit Komme..  [Comment]')},
             'O', 'string', 'default'),
            ({'code': 'array[SQ001]', 'full': _('Array [Unterfrage eins]'), 'abbreviated': _('Array [Unterfrage eins]')},
             'F', 'string', 'default'),
            ({'code': 'array[SQ002]', 'full': _('Array [Unterfrage zwei]'), 'abbreviated': _('Array [Unterfrage zwei]')},
             'F', 'string', 'default'),
            ({'code': 'arrayzehnpunktewahl[SQ001]', 'full': _('Array (Zehn Punkte Wahl) [Unterfrage eins]'), 'abbreviated': _('Array (Zehn Pun..  [Unterfrage eins]')},
             'B', 'string', 'default'),
            ({'code': 'arrayzehnpunktewahl[SQ002]', 'full': _('Array (Zehn Punkte Wahl) [Unterfrage zwei]'), 'abbreviated': _('Array (Zehn Pun..  [Unterfrage zwei]')},
             'B', 'string', 'default'),
            ({'code': 'arrayfunfpunktewahl[SQ001]', 'full': _('Array (Fünf Punkte Wahl) [Unterfrage eins]'), 'abbreviated': _('Array (Fünf Pun..  [Unterfrage eins]')},
             'A', 'string', 'default'),
            ({'code': 'arrayfunfpunktewahl[SQ002]', 'full': _('Array (Fünf Punkte Wahl) [Unterfrage zwei]'), 'abbreviated': _('Array (Fünf Pun..  [Unterfrage zwei]')},
             'A', 'string', 'default'),
            ({'code': 'arrayerhohengleichev[SQ001]', 'full': _('Array (Erhöhen/Gleiche/Verringern) [Unterfrage eins]'), 'abbreviated': _('Array (Erhöhen/..  [Unterfrage eins]')},
             'E', 'string', 'default'),
            ({'code': 'arrayerhohengleichev[SQ002]', 'full': _('Array (Erhöhen/Gleiche/Verringern) [Unterfrage zwei]'), 'abbreviated': _('Array (Erhöhen/..  [Unterfrage zwei]')},
             'E', 'string', 'default'),
            ({'code': 'arrayzahlen[SQ001_SQ001]', 'full': _('Array (Zahlen) [Unterfrage eins][Unterfrage eins]'), 'abbreviated': _('Array (Zahlen) [Unterfrage eins][Unterfrage eins]')},
             ':', 'string', 'default'),
            ({'code': 'arrayzahlen[SQ002_SQ001]', 'full': _('Array (Zahlen) [Unterfrage zwei][Unterfrage eins]'), 'abbreviated': _('Array (Zahlen) [Unterfrage zwei][Unterfrage eins]')},
             ':', 'string', 'default'),
            ({'code': 'arraytexte[SQ001_SQ001]', 'full': _('Array (Texte) [Unterfrage eins][Unterfrage eins]'), 'abbreviated': _('Array (Texte) [Unterfrage eins][Unterfrage eins]')},
             ';', 'string', 'default'),
            ({'code': 'arraytexte[SQ001_SQ002]', 'full': _('Array (Texte) [Unterfrage eins][Unterfrage zwei]'), 'abbreviated': _('Array (Texte) [Unterfrage eins][Unterfrage zwei]')},
             ';', 'string', 'default'),
            ({'code': 'arrayjaneinunsicher[SQ001]', 'full': _('Array (Ja/Nein/Unsicher) [Unterfrage eins]'), 'abbreviated': _('Array (Ja/Nein/..  [Unterfrage eins]')},
             'C', 'string', 'default'),
            ({'code': 'arrayjaneinunsicher[SQ002]', 'full': _('Array (Ja/Nein/Unsicher) [Unterfrage zwei]'), 'abbreviated': _('Array (Ja/Nein/..  [Unterfrage zwei]')},
             'C', 'string', 'default'),
            ({'code': 'arrayvonspalte[SQ001]', 'full': _('Array von Spalte [Unterfrage eins]'), 'abbreviated': _('Array von Spalte [Unterfrage eins]')},
             'H', 'string', 'default'),
            ({'code': 'arrayvonspalte[SQ002]', 'full': _('Array von Spalte [Unterfrage zwei]'), 'abbreviated': _('Array von Spalte [Unterfrage zwei]')},
             'H', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ001][1]', 'full': _('Array Duale Skala [Unterfrage eins][Scale 1]'), 'abbreviated': _('Array Duale Skala [Unterfrage eins][Scale 1]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ001][2]', 'full': _('Array Duale Skala [Unterfrage eins][Scale 2]'), 'abbreviated': _('Array Duale Skala [Unterfrage eins][Scale 2]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ002][1]', 'full': _('Array Duale Skala [Unterfrage zwei][Scale 1]'), 'abbreviated': _('Array Duale Skala [Unterfrage zwei][Scale 1]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ002][2]', 'full': _('Array Duale Skala [Unterfrage zwei][Scale 2]'), 'abbreviated': _('Array Duale Skala [Unterfrage zwei][Scale 2]')},
             '1', 'string', 'default'),
            ({'code': 'terminzeit', 'full': _('Terminzeit'), 'abbreviated': _('Terminzeit')},
             'D', 'datetime', '%Y-%m-%d %H:%M:%S'),
            ({'code': 'gleichung', 'full': _('Gleichung'), 'abbreviated': _('Gleichung')},
             '*', 'string', 'default'),
            ({'code': 'dateiupload', 'full': _('Datei-Upload'), 'abbreviated': _('Datei-Upload')},
             '|', 'string', 'default'),
            ({'code': 'dateiupload[filecount]', 'full': _('filecount - Datei-Upload'), 'abbreviated': _('filecount - Dat..')},
             '|', 'string', 'default'),
            ({'code': 'geschlecht', 'full': _('Geschlecht'), 'abbreviated': _('Geschlecht')},
             'G', 'string', 'default'),
            ({'code': 'sprachumschaltung', 'full': _('Sprachumschaltung'), 'abbreviated': _('Sprachumschaltung')},
             'I', 'string', 'default'),
            ({'code': 'mehrfachenumerischee[SQ001]', 'full': _('Mehrfache numerische Eingabe [Unterfrage eins]'), 'abbreviated': _('Mehrfache numer..  [Unterfrage eins]')},
             'K', 'number', 'default'),
            ({'code': 'mehrfachenumerischee[SQ002]', 'full': _('Mehrfache numerische Eingabe [Unterfrage zwei]'), 'abbreviated': _('Mehrfache numer..  [Unterfrage zwei]')},
             'K', 'number', 'default'),
            ({'code': 'numerischeeingabe', 'full': _('Numerische Eingabe'), 'abbreviated': _('Numerische Eingabe')},
             'N', 'number', 'default'),
            ({'code': 'rang[1]', 'full': _('Rang [Rank 1]'), 'abbreviated': _('Rang [Rank 1]')},
             'R', 'string', 'default'),
            ({'code': 'rang[2]', 'full': _('Rang [Rank 2]'), 'abbreviated': _('Rang [Rank 2]')},
             'R', 'string', 'default'),
            ({'code': 'textanzeige', 'full': _('Textanzeige'), 'abbreviated': _('Textanzeige')},
             'X', 'string', 'default'),
            ({'code': 'janein', 'full': _('Ja/Nein'), 'abbreviated': _('Ja/Nein')},
             'Y', 'string', 'default'),
            ({'code': 'reisigerfreitext', 'full': _('Reisiger Freitext'), 'abbreviated': _('Reisiger Freitext')},
             'U', 'string', 'default'),
            ({'code': 'langerfreiertext', 'full': _('Langer freier Text'), 'abbreviated': _('Langer freier Text')},
             'T', 'string', 'default'),
            ({'code': 'mehrfacherkurztext[SQ001]', 'full': _('Mehrfacher Kurztext [Unterfrage eins]'), 'abbreviated': _('Mehrfacher Kurz..  [Unterfrage eins]')},
             'Q', 'string', 'default'),
            ({'code': 'mehrfacherkurztext[SQ002]', 'full': _('Mehrfacher Kurztext [Unterfrage zwei]'), 'abbreviated': _('Mehrfacher Kurz..  [Unterfrage zwei]')},
             'Q', 'string', 'default'),
            ({'code': 'kurzerfreitext', 'full': _('Kurzer Freitext'), 'abbreviated': _('Kurzer Freitext')},
             'S', 'string', 'default'),
            ({'code': 'mehrfachauswahl[SQ001]', 'full': _('Mehrfachauswahl [Unterfrage eins]'), 'abbreviated': _('Mehrfachauswahl [Unterfrage eins]')},
             'M', 'string', 'default'),
            ({'code': 'mehrfachauswahl[SQ002]', 'full': _('Mehrfachauswahl [Unterfrage zwei]'), 'abbreviated': _('Mehrfachauswahl [Unterfrage zwei]')},
             'M', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ001]', 'full': _('Mehrfachauswahl mit Kommentaren [Unterfrage eins]'), 'abbreviated': _('Mehrfachauswahl..  [Unterfrage eins]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ001comment]', 'full': _('Mehrfachauswahl mit Kommentaren [Comment]'), 'abbreviated': _('Mehrfachauswahl..  [Comment]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ002]', 'full': _('Mehrfachauswahl mit Kommentaren [Unterfrage zwei]'), 'abbreviated': _('Mehrfachauswahl..  [Unterfrage zwei]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ002comment]', 'full': _('Mehrfachauswahl mit Kommentaren [Comment]'), 'abbreviated': _('Mehrfachauswahl..  [Comment]')},
             'P', 'string', 'default')
        ]

    def _asserts_elements_in_zipfile(self, zipped_file, group1, group2):
        # Assertions for first group
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group1.title), 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group1.title), 'Experimental_Protocol'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group1.title), 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group1.title), 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group1.title), 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group1.title), 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group1.title), 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group1.title), 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

        # Assertions for second group
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
    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content(self, mockServer):
        """Without reuse"""

        set_mocks1(mockServer)

        # Create questionnaire in NES
        # TODO (NES-991): already created in setUp
        dct = self._create_nes_questionnaire(self.root_component)

        # Create first patient/subject/subject_of_group besides those of setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct, responsible=self.user, token_id=2, subject_of_group=subject_of_group)

        # Create second patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct, responsible=self.user, token_id=3, subject_of_group=subject_of_group2)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
            'headings': ['code'], 'patient_selected': ['age*age'], 'responses': ['short'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*fileUpload*fileUpload'
            ]
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(os.path.join(
            input_export.BASE_DIRECTORY, 'Experiment_data', 'Group_' + self.group.title.lower(),
            'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
            self.survey.code + '_test-questionnaire_en.csv'), temp_dir
        )

        with open(os.path.join(
                temp_dir, input_export.BASE_DIRECTORY, 'Experiment_data',
                'Group_' + self.group.title.lower(), 'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv')
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
        dct = self._create_nes_questionnaire(self.root_component)

        # Create one more patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(self.group, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct, responsible=self.user, token_id=2, subject_of_group=subject_of_group)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
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
        """With reuse"""
        # by now: simply testing in browser is working (but, make this test ;)
        pass

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_two_groups_with_questionnaire_step_in_both_returns_correct_directory_structure(self, mockServer):
        set_mocks3(mockServer)

        # Create other group/experimental protocol
        root_component2 = ObjectsFactory.create_block(self.experiment)
        group2 = ObjectsFactory.create_group(self.experiment, root_component2)

        # Create questionnaire component (reuse Survey created in setUp)
        dct2 = self._create_nes_questionnaire(root_component2)

        # Create patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject)

        ObjectsFactory.create_questionnaire_response(
            dct=dct2, responsible=self.user, token_id=2, subject_of_group=subject_of_group2)

        self.append_session_variable('group_selected_list', [str(self.group.id), str(group2.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        self._asserts_elements_in_zipfile(zipped_file, self.group, group2)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_has_correct_header_fields_in_questionnaire_responses_file(self, mockServer):
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        # TODO (NES-991): see false positive when take off headings in line 783 of views
        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks4(mockServer)
            if heading_type != 'code':
                update_mocks4_full_and_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to_experiment[]': [
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*acquisitiondate*acquisitiondate',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*firstQuestion*firstQuestion',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*secondQuestion*secondQuestion',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*fileUpload*fileUpload'
                ],
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            zipped_file = self.get_zipped_file(response)
            zipped_file.extract(os.path.join(
                    input_export.BASE_DIRECTORY, 'Experiment_data', 'Group_' + self.group.title.lower(),
                    'Per_questionnaire', 'Step_1_QUESTIONNAIRE', self.survey.code + '_test-questionnaire_en.csv'
                ), temp_dir
            )

            with open(os.path.join(
                        temp_dir, input_export.BASE_DIRECTORY, 'Experiment_data', 'Group_' + self.group.title.lower(),
                        'Per_questionnaire', 'Step_1_QUESTIONNAIRE', self.survey.code + '_test-questionnaire_en.csv'
                    )) as file:
                csv_line1 = next(csv.reader(file))
                self.assertEqual(len(csv_line1), 6)
                if heading_type == 'code':
                    self.assertEquals(
                        csv_line1,
                        ['participant_code', 'age', 'acquisitiondate', 'firstQuestion', 'secondQuestion', 'fileUpload'])
                else:
                    self.assertEquals(
                        csv_line1,
                        # TODO (NES-991): extends some string to test abbreviated
                        [
                            'participant_code', _('Age'), _('Acquisition date:'), _('First Question'),
                            _('Second Question'), _('File Upload')
                        ]
                    )

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
            dct=self.data_configuration_tree, responsible=self.user, token_id=2, subject_of_group=subject_of_group2)

        self.append_session_variable('group_selected_list', [str(self.group.id), str(group2.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
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

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Change questionnaire respose date for testing
        self.questionnaire_response.date = date(2016, 7, 7)
        self.questionnaire_response.save()

        # Post data to view: data style that is posted to export_view in
        # template
        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks4(mockServer)
            if heading_type != 'code':
                update_mocks4_full_and_abbreviated(mockServer)
            data = {
                'per_participant': ['on'],
                'per_questionnaire': ['on'],
                'action': ['run'],
                'headings': [heading_type],
                'to_experiment[]': [
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*acquisitiondate*acquisitiondate',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*firstQuestion*firstQuestion',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*secondQuestion*secondQuestion',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                    '*Test questionnaire*fileUpload*fileUpload'
                ],
                'patient_selected': ['age*age'],
                'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            zipped_file = self.get_zipped_file(response)
            zipped_file.extract(os.path.join(
                    input_export.BASE_DIRECTORY, 'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'), temp_dir)

            with open(os.path.join(
                    temp_dir, input_export.BASE_DIRECTORY, 'Experiment_data',
                    'Group_' + self.group.title.lower(), 'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
            )) as file:
                csvreader = csv.reader(file)
                rows = []
                for row in csvreader:
                    rows.append(row)
                self.assertEqual(
                    rows[1][1], ExportParticipantsTest.subject_age(
                        self.patient.date_birth, self.questionnaire_response))

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
                '0*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
            'license': '0'
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(os.path.join(input_export.BASE_DIRECTORY, 'Participants.csv'), temp_dir)

        with open(os.path.join(
                temp_dir, input_export.BASE_DIRECTORY, 'Participants.csv'
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
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1) +
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
                input_export.BASE_DIRECTORY,
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
                    input_export.BASE_DIRECTORY,
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
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                +
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
                input_export.BASE_DIRECTORY,
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
                    input_export.BASE_DIRECTORY,
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
            self.experiment, Component.GENERIC_DATA_COLLECTION, kwargs={'it': it})

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, gdc)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group)
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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

        # We have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "generic_data_collection")[0]

        generic_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = generic_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'Generic_Data_Collection_1',
            os.path.basename(gdcf.file.name), zipped_file)
        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1',
            os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_digital_game_phase_data_colletion(self):
        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree})

        # Include dgp component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, dgp)

        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' digital game data file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(dct, self.subject_of_group)

        dgpf = ObjectsFactory.create_digital_game_phase_file(dgp_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'], 'per_goalkeeper_game_data': ['on'],
            'per_additional_data': ['on'], 'headings': ['code'], 'patient_selected': ['age*age'],
            'action': ['run'], 'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # We have only the digital_game_phase step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "digital_game_phase")[0]

        digital_game_phase_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = digital_game_phase_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'DigitalGamePhaseData_1', os.path.basename(dgpf.file.name), zipped_file)
        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1', os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_eeg(self):
        # Create eeg component
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(self.experiment, Component.EEG, kwargs={'eeg_set': eeg_set})

        # Include eeg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, eeg_comp)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' eeg file
        eegdata = ObjectsFactory.create_eeg_data(dct, self.subject_of_group, eeg_set)
        eegf = ObjectsFactory.create_eeg_file(eegdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)
        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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

        # We have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "eeg")[0]
        eeg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = eeg_conf.component
        step_number = path[-1][4]
        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'EEGData_1',
            os.path.basename(eegf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1',
            os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_emg(self):
        # Create emg component
        self.manufacturer = ObjectsFactory.create_manufacturer()
        self.software = ObjectsFactory.create_software(self.manufacturer)
        self.software_version = ObjectsFactory.create_software_version(self.software)
        self.tag_emg = ObjectsFactory.create_tag('EMG')
        emg_set = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)
        emg_comp = ObjectsFactory.create_component(self.experiment, Component.EMG, kwargs={'emg_set': emg_set})

        # Include emg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, emg_comp)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' emg file
        emgdata = ObjectsFactory.create_emg_data_collection_data(dct, self.subject_of_group, emg_set)
        emgf = ObjectsFactory.create_emg_data_collection_file(emgdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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

        # We have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "emg")[0]
        emg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = emg_conf.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'EMGData_1', os.path.basename(emgf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1', os.path.basename(adf.file.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_tms(self):
        # Create tms component
        tms_set = ObjectsFactory.create_tms_setting(self.experiment)
        tms_comp = ObjectsFactory.create_component(self.experiment, Component.TMS, kwargs={'tms_set': tms_set})

        # Include tms component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, tms_comp)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        doic = DirectionOfTheInducedCurrent.objects.create(name="Direction of Induced Current")
        coilor = CoilOrientation.objects.create(name="Coil Orientation")

        tmsdataaux = TMSData.objects.create(
            tms_setting=tms_set, data_configuration_tree=dct, subject_of_group=self.subject_of_group,
            coil_orientation=coilor, description="Teste TMS", direction_of_induced_current=doic)

        brainareasystem = BrainAreaSystem.objects.create(name='Lobo frontal')

        brainarea = BrainArea.objects.create(name='Lobo frontal', brain_area_system=brainareasystem)

        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, 'image.bin'), 'wb') as f:
            f.write(b'carambola')
        temp_file = f.name

        tms_local_sys = TMSLocalizationSystem.objects.create(
            name="TMS name", brain_area=brainarea, tms_localization_system_image=temp_file)

        hotspot = HotSpot.objects.create(
            tms_data=tmsdataaux, name="TMS Data Collection File", tms_localization_system=tms_local_sys)

        ObjectsFactory.create_hotspot_data_collection_file(hotspot)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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
        group1 = ObjectsFactory.create_group(self.experiment, root_component1)
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = ObjectsFactory.create_subject_of_group(group1, subject1)

        # Create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(self.experiment, Component.GENERIC_DATA_COLLECTION,kwargs={'it': it})

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, gdc)
        component_config1 = ObjectsFactory.create_component_configuration(root_component1, gdc)

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(dct, self.subject_of_group)
        gdc_data1 = ObjectsFactory.create_generic_data_collection_data(dct1, subject_of_group1)

        ObjectsFactory.create_generic_data_collection_file(gdc_data)
        ObjectsFactory.create_generic_data_collection_file(gdc_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id), str(group1.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'], 'per_generic_data': ['on'],
            'per_additional_data': ['on'], 'headings': ['code'], 'patient_selected': ['age*age'],
            'action': ['run'], 'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)
        zipped_file = self.get_zipped_file(response)

        for path in create_list_of_trees(self.group.experimental_protocol,'generic_data_collection'):
            generic_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(
                step_number, component_step, 'Generic_Data_Collection_1', 'file.bin', zipped_file)

            self.assert_per_participant_step_file_exists(
                step_number, component_step, 'AdditionalData_1', 'file.bin', zipped_file)

        for path in create_list_of_trees(
                group1.experimental_protocol, 'generic_data_collection'):
            generic_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(
                step_number, component_step, 'Generic_Data_Collection_1', 'file.bin', zipped_file)

            self.assert_per_participant_step_file_exists(
                step_number, component_step, 'AdditionalData_1', 'file.bin', zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_goalkeeper_game_data_2_groups(self):
        # Create second group; create patient/subject/subject_of_group
        # TODO (NES-987): use objects created in setUp
        root_component1 = ObjectsFactory.create_block(self.experiment)
        group1 = ObjectsFactory.create_group(self.experiment, root_component1)
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = ObjectsFactory.create_subject_of_group(group1, subject1)

        # Create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree})

        # Include dgp component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, dgp)
        component_config1 = ObjectsFactory.create_component_configuration(root_component1, dgp)

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' data game phase collection file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(dct, self.subject_of_group)

        dgp_data1 = ObjectsFactory.create_digital_game_phase_data(dct1, subject_of_group1)

        ObjectsFactory.create_digital_game_phase_file(dgp_data)
        ObjectsFactory.create_digital_game_phase_file(dgp_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id), str(group1.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'], 'per_goalkeeper_game_data': ['on'],
            'headings': ['code'], 'filesformat': ['csv'], 'responses': ['short'], 'patient_selected': ['age*age'],
            'action': ['run']
        }
        self.client.post(reverse('export_view'), data)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_step_additional_data(self):
        # Create generic data collection (gdc) component, it could been any data collection
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(self.experiment, Component.GENERIC_DATA_COLLECTION,kwargs={'it': it})

        # Create a file and add it as an additional file of the step
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'stepadditionaldata.bin'), 'wb') as f:
                f.write(b'carambola')
                with File(open(f.name, 'rb')) as file:
                    ComponentAdditionalFile.objects.create(component=gdc, file=file)

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, gdc)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(dct, self.subject_of_group)
        ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this subject of group
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'], 'per_generic_data': ['on'],
            'per_additional_data': ['on'], 'headings': ['code'], 'patient_selected': ['age*age'],
            'action': ['run'], 'responses': ['short']
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

        self.assert_step_data_files_exists(
            step_number, component_step, 'AdditionalData', os.path.basename(f.name), zipped_file)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_stimulus_media_file(self):
        # Create a stimulus component
        stimulus_type = ObjectsFactory.create_stimulus_type()

        with tempfile.TemporaryDirectory() as tmpdirname:
            f = ObjectsFactory.create_binary_file(tmpdirname)

            with File(open(f.name, 'rb')) as file:
                stimulus = ObjectsFactory.create_component(
                    self.experiment, Component.STIMULUS,
                    kwargs={'stimulus_type': stimulus_type, 'media_file': file})

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, stimulus)
        ObjectsFactory.create_data_configuration_tree(component_config)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'], 'per_generic_data': ['on'],
            'per_stimulus_data': ['on'], 'per_additional_data': ['on'], 'headings': ['code'],
            'patient_selected': ['age*age'], 'action': ['run'], 'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        # Get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # We have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "stimulus")[0]
        stimulus_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = stimulus_component_configuration.component
        step_number = path[-1][4]

        self.assert_step_data_files_exists(
            step_number, component_step, '', os.path.basename(f.name), zipped_file)

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

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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
            os.path.join(input_export.BASE_DIRECTORY, 'Participant_data', 'Participants.csv'), temp_dir)

        with open(os.path.join(temp_dir, input_export.BASE_DIRECTORY, 'Participant_data', 'Participants.csv')) as file:
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

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

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
        zipped_file.extract(os.path.join(input_export.BASE_DIRECTORY, 'Participant_data', 'Participants.csv'), temp_dir)

        with open(os.path.join(temp_dir, input_export.BASE_DIRECTORY, 'Participant_data', 'Participants.csv')) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1], self.subject_age(self.patient.date_birth)
            )

        shutil.rmtree(temp_dir)


class ExportParticipantsTest(ExportTestCase):

    def setUp(self):
        super(ExportParticipantsTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_without_questionnaires_returns_zipped_file(self):
        """Test created when exporting participants, without questionnaires
        avulsely answered by them, gave yellow screen. See Jira Issue NES-864.
        """
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        self.get_zipped_file(response)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('export.export.ExportExecution.get_directory_base')
    def test_create_directory_fails_returns_error_message(self, get_directory_base_mock):
        get_directory_base_mock.return_value = '/non/existent/path'
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data, follow=True)
        message = str(list(response.context['messages'])[0])

        self.assertEqual(message, _('Base path does not exist'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('export.export.ExportExecution.get_directory_base')
    def test_create_directory_fails_removes_export_dir(self, get_directory_base_mock):
        get_directory_base_mock.return_value = '/non/existent/path'
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        self.client.post(reverse('export_view'), data, follow=True)

        export = Export.objects.first()
        self.assertFalse(os.path.exists(
            os.path.join(TEMP_MEDIA_ROOT, EXPORT_DIRECTORY, str(self.user.id), str(export.id))))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('export.export.ExportExecution.is_input_data_consistent')
    def test_input_data_is_inconsistent_returns_error_message(self, is_input_data_consistent_mock):
        is_input_data_consistent_mock.return_value = False
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data, follow=True)
        message = str(list(response.context['messages'])[0])

        self.assertEqual(message, _('Inconsistent data read from json file'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('export.export.ExportExecution.is_input_data_consistent')
    def test_input_data_is_inconsistent_removes_export_dir(self, is_input_data_consistent_mock):
        is_input_data_consistent_mock.return_value = False
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        self.client.post(reverse('export_view'), data, follow=True)

        export = Export.objects.first()
        self.assertFalse(os.path.exists(
            os.path.join(TEMP_MEDIA_ROOT, EXPORT_DIRECTORY, str(self.user.id), str(export.id))))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('export.export.ExportExecution.create_export_directory')
    def test_create_export_directory_fails_return_error_message(self, create_export_directory_mock):
        pass  # continue here when come back to NES-983

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_age_is_age_at_export_date_if_no_questionnaire_response(self):
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(os.path.join(input_export.BASE_DIRECTORY, 'Participants.csv'), temp_dir)

        with open(os.path.join(temp_dir, input_export.BASE_DIRECTORY, 'Participants.csv')) as file:
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


class ExportSelectionTest(ExportTestCase):

    def setUp(self):
        super(ExportSelectionTest, self).setUp()

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

    def test_experiment_selection_without_select_group(self):

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

    def test_experiment_selection_appends_license_to_request_session_and_redirects_to_export_view(self):
        data = {
            'id_research_projects': self.experiment.research_project.id,
            'id_experiments': self.experiment.id,
            'group_selected': self.group.id,
            'license': 0,
            'action': 'next-step-participants'
        }
        response = self.client.post(reverse('experiment_selection'), data)

        self.assertRedirects(response, '/export/view/', status_code=302, target_status_code=200)
        self.assertIn('license', self.client.session)
        self.assertEqual(self.client.session['license'], '0')


class ExportFrictionlessDataTest(ExportTestCase):

    def setUp(self):
        super(ExportFrictionlessDataTest, self).setUp()

        # Redirect sys.stdout to avoid messages during test.
        self.stdout_bk, sys.stdout = sys.stdout, open('/dev/null', 'w+')
        # Redirect sys.stderr to avoid a RuntimeWarning when calling
        # read_raw_egi method experiment view
        self.stderr_bk, sys.stderr = sys.stderr, open('/dev/null', 'w+')

    def tearDown(self):
        # Restore sys.stdout, sys.stderr
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.stdout_bk
        sys.stderr = self.stderr_bk

        self.client.logout()

    def _create_eeg_export_data(self):
        # Create eeg component (could be other component type or more than one component)
        self.eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(self.experiment, Component.EEG, kwargs={'eeg_set': self.eeg_set})

        # Include eeg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, eeg_comp)
        # self.dct to be used in other test
        self.dct_eeg = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' eeg file
        eegdata = ObjectsFactory.create_eeg_data(self.dct_eeg, self.subject_of_group, self.eeg_set)
        ObjectsFactory.create_eeg_file(eegdata)

    def _create_tms_export_data(self, temp_dir):
        tms_set = ObjectsFactory.create_tms_setting(self.experiment)
        tms_comp = ObjectsFactory.create_component(self.experiment, Component.TMS, kwargs={'tms_set': tms_set})

        # Include tms component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, tms_comp)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        doic = DirectionOfTheInducedCurrent.objects.create(name="Direction of Induced Current")
        coilor = CoilOrientation.objects.create(name="Coil Orientation")

        tmsdata = TMSData.objects.create(
            tms_setting=tms_set, data_configuration_tree=dct, subject_of_group=self.subject_of_group,
            coil_orientation=coilor, description="Teste TMS", direction_of_induced_current=doic)

        brainareasystem = BrainAreaSystem.objects.create(name='Lobo frontal')
        brainarea = BrainArea.objects.create(name='Lobo frontal', brain_area_system=brainareasystem)

        with open(os.path.join(temp_dir, 'image.bin'), 'wb') as f:
            f.write(b'carambola')
        temp_file = f.name
        tms_local_sys = TMSLocalizationSystem.objects.create(
            name="TMS name", brain_area=brainarea, tms_localization_system_image=temp_file)

        hotspot = HotSpot.objects.create(
            tms_data=tmsdata, name="TMS Data Collection File", tms_localization_system=tms_local_sys)
        ObjectsFactory.create_hotspot_data_collection_file(hotspot)

    def _create_emg_export_data(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        self.emg_set = ObjectsFactory.create_emg_setting(self.experiment, software_version)
        emg_comp = ObjectsFactory.create_component(self.experiment, Component.EMG, kwargs={'emg_set': self.emg_set})

        # Include emg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, emg_comp)
        self.dct_emg = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' emg file
        self.emgdata = ObjectsFactory.create_emg_data_collection_data(self.dct_emg, self.subject_of_group, self.emg_set)
        ObjectsFactory.create_emg_data_collection_file(self.emgdata)

    def _create_goalkeeper_game_export_data(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)
        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree})
        component_config = ObjectsFactory.create_component_configuration(self.root_component, dgp)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dgp_data = ObjectsFactory.create_digital_game_phase_data(dct, self.subject_of_group)
        dgp_file = ObjectsFactory.create_digital_game_phase_file(dgp_data, 'file_dgp.bin')

        return dgp_file

    def _create_questionnaire_export_data(self):
        # Create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        self.questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': self.survey})
        # Include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, self.questionnaire)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # Add response's participant to limesurvey survey and the references
        # in our db
        ObjectsFactory.create_questionnaire_response(
            dct=dct, responsible=self.user, token_id=1, subject_of_group=self.subject_of_group)

    def _assert_basic_per_experiment_data(self, json_data):
        for item in ['title', 'name', 'description', 'created', 'homepage']:
            self.assertIn(item, json_data, '\'' + item + '\'' + ' not in ' + str(json_data))

        name = slugify(self.experiment.title)
        self.assertEqual(self.experiment.title, json_data['title'])
        self.assertEqual(name, json_data['name'])
        self.assertEqual(self.experiment.description, json_data['description'])
        day = json_data['created'].split(' ')[0]  # Get only the day to avoid test not passing
        self.assertEqual(datetime.now().strftime('%Y-%m-%d'), day)
        # TODO (NES-987): see how to get testserver from TestCase class or other place,
        #  and https/http url part
        self.assertIn('testserver/experiments/' + name, json_data['homepage'])

    def _assert_basic_per_participant_data(self, json_data):
        for item in ['title', 'name', 'description', 'created']:
            self.assertIn(item, json_data, '\'' + item + '\'' + ' not in ' + str(json_data))

        title = 'Questionnaires Answered by Participants Outside Experiment Scope'
        name = slugify(title)
        description = 'Export made \"Per Participant\": the files contain metadata and responses of ' \
                      'questionnaires filled outside any experiment in the system. They can be entrance ' \
                      'questionnaires.'
        day = json_data['created'].split(' ')[0]  # Get only the day to avoid test not passing
        self.assertEqual(title, json_data['title'])
        self.assertEqual(name, json_data['name'])
        self.assertEqual(description, json_data['description'])
        self.assertEqual(datetime.now().strftime('%Y-%m-%d'), day)

    def _assert_experiment_table_schema(self, resource_schema):
        self.assertIn(
            {'name': 'Study', 'title': 'Study', 'type': 'string', 'format': 'default'},
            resource_schema['fields'])
        self.assertIn(
            {'name': 'Study description', 'title': 'Study description', 'type': 'string', 'format': 'default'},
            resource_schema['fields'])
        self.assertIn(
            {'name': 'Experiment Title', 'title': 'Experiment Title', 'type': 'string', 'format': 'default'},
            resource_schema['fields'])
        self.assertIn(
            {
                'name': 'Experiment description', 'title': 'Experiment description', 'type': 'string',
                'format': 'default'
            }, resource_schema['fields'])
        self.assertIn(
            {'name': 'Start date', 'title': 'Start date', 'type': 'date', 'format': 'default'},
            resource_schema['fields'])
        self.assertIn(
            {'name': 'End date', 'title': 'End date', 'type': 'date', 'format': 'default'},
            resource_schema['fields'])

    @staticmethod
    def _set_validation_for_goodtables(path, heading_type):
        skip_checks = ['duplicate-row']  # For questionnaire metadata files
        if heading_type == 'full' or 'abbreviated':
            # For questionnaire responses: there is one header repeated for one question type.
            # We don't solve this by now.
            skip_checks.append('duplicate-header')
        return validate(path, skip_checks=skip_checks)

    def _assert_goodtables(self, report):
        errors = report['errors'] if 'errors' in report else []
        table_errors = []
        for table in report['tables']:
            if table['errors']:
                table_errors.append((table['source'], table['errors']))
        self.assertTrue(
            report['valid'],
            'Errors: ' + str(errors) + '. Table errors: ' + str(table_errors))

    @staticmethod
    def _get_name_title(heading_type, field):
        title = ''
        if heading_type == 'code':
            title = field['header']
        elif heading_type == 'full':
            title = field['description']
        elif heading_type == 'abbreviated':
            title = abbreviated_data(field['description'])

        # It's always 'participant_code' independently of heading type
        if field['header'] == 'participant_code':
            title = field['header']

        return title

    def _assert_participants_related_fields_table_schema(self, resource_schema, heading_type, fields):
        titles = []
        types = []
        # First append for testing later: when heading_type == 'abbreviated' it's
        # necessary to update duplicates below
        for field in fields:
            dict_item = next(item for item in fields if item['header'] == field['header'])
            titles.append(self._get_name_title(heading_type, dict_item))
            types.append(field['json_data_type'])

        if heading_type == 'abbreviated':
            ExportExecution.update_duplicates(titles)

        for title, type in zip(titles, types):
            self.assertIn(
                {'name': title, 'title': title, 'type': type, 'format': 'default'},
                resource_schema['fields'], 'Failed for heading type ' + heading_type)

    @staticmethod
    def _set_post_data(*data_collections):
        # Data style that is posted to export_view in template
        post_data = {
            'per_questionnaire': ['on'], 'per_participant': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'], 'patient_selected': ['age*age'],
            'action': ['run'], 'responses': ['short']
        }
        for data_collection in data_collections:
            post_data[data_collection] = ['on']

        return post_data

    @staticmethod
    def _set_all_questions():
        return [
            ({'code': 'acquisitiondate', 'full': _('Acquisition date:'), 'abbreviated': _('Acquisition date:')},
             'D', 'datetime', '%Y-%m-%d %H:%M:%S'),
            ({'code': 'funfpunktewahl', 'full': _('Fünf Punkte Wahl'), 'abbreviated': _('Fünf Punkte Wahl')},
             '5', 'string', 'default'),
            ({'code': 'dropdownliste', 'full': _('Dropdown Liste'), 'abbreviated': _('Dropdown Liste')},
             '!', 'string', 'default'),
            ({'code': 'listeradio', 'full': _('Liste (radio)'), 'abbreviated': _('Liste (radio)')},
             'L', 'string', 'default'),
            ({'code': 'listemitkommentar', 'full': _('Liste mit Kommentar'), 'abbreviated': _('Liste mit Komme..')},
             'O', 'string', 'default'),
            ({'code': 'listemitkommentar[comment]', 'full': _('Liste mit Kommentar [Comment]'), 'abbreviated': _('Liste mit Komme..  [Comment]')},
             'O', 'string', 'default'),
            ({'code': 'array[SQ001]', 'full': _('Array [Unterfrage eins]'), 'abbreviated': _('Array [Unterfrage eins]')},
             'F', 'string', 'default'),
            ({'code': 'array[SQ002]', 'full': _('Array [Unterfrage zwei]'), 'abbreviated': _('Array [Unterfrage zwei]')},
             'F', 'string', 'default'),
            ({'code': 'arrayzehnpunktewahl[SQ001]', 'full': _('Array (Zehn Punkte Wahl) [Unterfrage eins]'), 'abbreviated': _('Array (Zehn Pun..  [Unterfrage eins]')},
             'B', 'string', 'default'),
            ({'code': 'arrayzehnpunktewahl[SQ002]', 'full': _('Array (Zehn Punkte Wahl) [Unterfrage zwei]'), 'abbreviated': _('Array (Zehn Pun..  [Unterfrage zwei]')},
             'B', 'string', 'default'),
            ({'code': 'arrayfunfpunktewahl[SQ001]', 'full': _('Array (Fünf Punkte Wahl) [Unterfrage eins]'), 'abbreviated': _('Array (Fünf Pun..  [Unterfrage eins]')},
             'A', 'string', 'default'),
            ({'code': 'arrayfunfpunktewahl[SQ002]', 'full': _('Array (Fünf Punkte Wahl) [Unterfrage zwei]'), 'abbreviated': _('Array (Fünf Pun..  [Unterfrage zwei]')},
             'A', 'string', 'default'),
            ({'code': 'arrayerhohengleichev[SQ001]', 'full': _('Array (Erhöhen/Gleiche/Verringern) [Unterfrage eins]'), 'abbreviated': _('Array (Erhöhen/..  [Unterfrage eins]')},
             'E', 'string', 'default'),
            ({'code': 'arrayerhohengleichev[SQ002]', 'full': _('Array (Erhöhen/Gleiche/Verringern) [Unterfrage zwei]'), 'abbreviated': _('Array (Erhöhen/..  [Unterfrage zwei]')},
             'E', 'string', 'default'),
            ({'code': 'arrayzahlen[SQ001_SQ001]', 'full': _('Array (Zahlen) [Unterfrage eins][Unterfrage eins]'), 'abbreviated': _('Array (Zahlen) [Unterfrage eins][Unterfrage eins]')},
             ':', 'string', 'default'),
            ({'code': 'arrayzahlen[SQ002_SQ001]', 'full': _('Array (Zahlen) [Unterfrage zwei][Unterfrage eins]'), 'abbreviated': _('Array (Zahlen) [Unterfrage zwei][Unterfrage eins]')},
             ':', 'string', 'default'),
            ({'code': 'arraytexte[SQ001_SQ001]', 'full': _('Array (Texte) [Unterfrage eins][Unterfrage eins]'), 'abbreviated': _('Array (Texte) [Unterfrage eins][Unterfrage eins]')},
             ';', 'string', 'default'),
            ({'code': 'arraytexte[SQ001_SQ002]', 'full': _('Array (Texte) [Unterfrage eins][Unterfrage zwei]'), 'abbreviated': _('Array (Texte) [Unterfrage eins][Unterfrage zwei]')},
             ';', 'string', 'default'),
            ({'code': 'arrayjaneinunsicher[SQ001]', 'full': _('Array (Ja/Nein/Unsicher) [Unterfrage eins]'), 'abbreviated': _('Array (Ja/Nein/..  [Unterfrage eins]')},
             'C', 'string', 'default'),
            ({'code': 'arrayjaneinunsicher[SQ002]', 'full': _('Array (Ja/Nein/Unsicher) [Unterfrage zwei]'), 'abbreviated': _('Array (Ja/Nein/..  [Unterfrage zwei]')},
             'C', 'string', 'default'),
            ({'code': 'arrayvonspalte[SQ001]', 'full': _('Array von Spalte [Unterfrage eins]'), 'abbreviated': _('Array von Spalte [Unterfrage eins]')},
             'H', 'string', 'default'),
            ({'code': 'arrayvonspalte[SQ002]', 'full': _('Array von Spalte [Unterfrage zwei]'), 'abbreviated': _('Array von Spalte [Unterfrage zwei]')},
             'H', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ001][1]', 'full': _('Array Duale Skala [Unterfrage eins][Scale 1]'), 'abbreviated': _('Array Duale Skala [Unterfrage eins][Scale 1]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ001][2]', 'full': _('Array Duale Skala [Unterfrage eins][Scale 2]'), 'abbreviated': _('Array Duale Skala [Unterfrage eins][Scale 2]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ002][1]', 'full': _('Array Duale Skala [Unterfrage zwei][Scale 1]'), 'abbreviated': _('Array Duale Skala [Unterfrage zwei][Scale 1]')},
             '1', 'string', 'default'),
            ({'code': 'arraydualeskala[SQ002][2]', 'full': _('Array Duale Skala [Unterfrage zwei][Scale 2]'), 'abbreviated': _('Array Duale Skala [Unterfrage zwei][Scale 2]')},
             '1', 'string', 'default'),
            ({'code': 'terminzeit', 'full': _('Terminzeit'), 'abbreviated': _('Terminzeit')},
             'D', 'datetime', '%Y-%m-%d %H:%M:%S'),
            ({'code': 'gleichung', 'full': _('Gleichung'), 'abbreviated': _('Gleichung')},
             '*', 'string', 'default'),
            ({'code': 'dateiupload', 'full': _('Datei-Upload'), 'abbreviated': _('Datei-Upload')},
             '|', 'string', 'default'),
            ({'code': 'dateiupload[filecount]', 'full': _('filecount - Datei-Upload'), 'abbreviated': _('filecount - Dat..')},
             '|', 'string', 'default'),
            ({'code': 'geschlecht', 'full': _('Geschlecht'), 'abbreviated': _('Geschlecht')},
             'G', 'string', 'default'),
            ({'code': 'sprachumschaltung', 'full': _('Sprachumschaltung'), 'abbreviated': _('Sprachumschaltung')},
             'I', 'string', 'default'),
            ({'code': 'mehrfachenumerischee[SQ001]', 'full': _('Mehrfache numerische Eingabe [Unterfrage eins]'), 'abbreviated': _('Mehrfache numer..  [Unterfrage eins]')},
             'K', 'number', 'default'),
            ({'code': 'mehrfachenumerischee[SQ002]', 'full': _('Mehrfache numerische Eingabe [Unterfrage zwei]'), 'abbreviated': _('Mehrfache numer..  [Unterfrage zwei]')},
             'K', 'number', 'default'),
            ({'code': 'numerischeeingabe', 'full': _('Numerische Eingabe'), 'abbreviated': _('Numerische Eingabe')},
             'N', 'number', 'default'),
            ({'code': 'rang[1]', 'full': _('Rang [Rank 1]'), 'abbreviated': _('Rang [Rank 1]')},
             'R', 'string', 'default'),
            ({'code': 'rang[2]', 'full': _('Rang [Rank 2]'), 'abbreviated': _('Rang [Rank 2]')},
             'R', 'string', 'default'),
            ({'code': 'textanzeige', 'full': _('Textanzeige'), 'abbreviated': _('Textanzeige')},
             'X', 'string', 'default'),
            ({'code': 'janein', 'full': _('Ja/Nein'), 'abbreviated': _('Ja/Nein')},
             'Y', 'string', 'default'),
            ({'code': 'reisigerfreitext', 'full': _('Reisiger Freitext'), 'abbreviated': _('Reisiger Freitext')},
             'U', 'string', 'default'),
            ({'code': 'langerfreiertext', 'full': _('Langer freier Text'), 'abbreviated': _('Langer freier Text')},
             'T', 'string', 'default'),
            ({'code': 'mehrfacherkurztext[SQ001]', 'full': _('Mehrfacher Kurztext [Unterfrage eins]'), 'abbreviated': _('Mehrfacher Kurz..  [Unterfrage eins]')},
             'Q', 'string', 'default'),
            ({'code': 'mehrfacherkurztext[SQ002]', 'full': _('Mehrfacher Kurztext [Unterfrage zwei]'), 'abbreviated': _('Mehrfacher Kurz..  [Unterfrage zwei]')},
             'Q', 'string', 'default'),
            ({'code': 'kurzerfreitext', 'full': _('Kurzer Freitext'), 'abbreviated': _('Kurzer Freitext')},
             'S', 'string', 'default'),
            ({'code': 'mehrfachauswahl[SQ001]', 'full': _('Mehrfachauswahl [Unterfrage eins]'), 'abbreviated': _('Mehrfachauswahl [Unterfrage eins]')},
             'M', 'string', 'default'),
            ({'code': 'mehrfachauswahl[SQ002]', 'full': _('Mehrfachauswahl [Unterfrage zwei]'), 'abbreviated': _('Mehrfachauswahl [Unterfrage zwei]')},
             'M', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ001]', 'full': _('Mehrfachauswahl mit Kommentaren [Unterfrage eins]'), 'abbreviated': _('Mehrfachauswahl..  [Unterfrage eins]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ001comment]', 'full': _('Mehrfachauswahl mit Kommentaren [Comment]'), 'abbreviated': _('Mehrfachauswahl..  [Comment]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ002]', 'full': _('Mehrfachauswahl mit Kommentaren [Unterfrage zwei]'), 'abbreviated': _('Mehrfachauswahl..  [Unterfrage zwei]')},
             'P', 'string', 'default'),
            ({'code': 'mehrfachauswahlmitko[SQ002comment]', 'full': _('Mehrfachauswahl mit Kommentaren [Comment]'), 'abbreviated': _('Mehrfachauswahl..  [Comment]')},
             'P', 'string', 'default')
        ]

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_creates_content_dirs_inside_data_directory(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)
        data_dir = re.compile('^data')
        self.assertTrue(
            all(data_dir.match(element) for element in zipped_file.namelist()),
            'data dir not found in: ' + str(zipped_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_creates_datapackage_json_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)
        self.assertTrue(any('datapackage.json' in element for element in zipped_file.namelist()),
                        'datapackage.json not found in: ' + str(zipped_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_basic_content_to_datapackage_json_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        self._assert_basic_per_experiment_data(json_data)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_experiment_contributors_to_datapackage_json_file(self):
        self._create_eeg_export_data()
        contributor1 = self.research_project.owner
        contributor2 = ObjectsFactory.create_experiment_researcher(self.experiment).researcher
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('contributors', json_data)
        self.assertIn({
            'title': contributor1.first_name + ' ' + contributor1.last_name,
            'email': contributor1.email
        }, json_data['contributors'])
        self.assertIn({
            'title': contributor2.first_name + ' ' + contributor2.last_name,
            'email': contributor2.email
        }, json_data['contributors'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_default_license_to_datapackage_json_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('licenses', json_data)
        self.assertIn({
            'name': 'CC', 'path': 'https://creativecommons.org', 'title': 'Creative Commons'
        }, json_data['licenses'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_creative_commons_license_to_datapackage_json_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '1')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('licenses', json_data)
        self.assertIn({
            'name': '©', 'path': 'https://simple.wikipedia.org/wiki/Copyright', 'title': 'Copyright'
        }, json_data['licenses'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_resources_field_to_datapackage_json_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('resources', json_data)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_basic_experiment_data_file_info_to_datapackage_json_resources_field(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        experiment_resource = next(item for item in json_data['resources'] if item['name'] == 'Experiment')

        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in experiment_resource:
            experiment_resource.pop('schema')
        test_dict = {
            'name': 'Experiment', 'title': 'Experiment', 'path': 'data/Experiment_data/Experiment.csv',
            'format': 'csv', 'mediatype': 'text/csv', 'encoding': 'UTF-8',
            'profile': 'tabular-data-resource'
        }
        self.assertEqual(
            test_dict, experiment_resource,
            str(test_dict) + ' not equal ' + str(experiment_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_experiment_table_schema_info_to_datapackage_json_experiment_resource(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        experiment_resource = next(item for item in json_data['resources'] if item['name'] == 'Experiment')

        self.assertIn('schema', experiment_resource)
        self.assertIn('fields', experiment_resource['schema'])
        self._assert_experiment_table_schema(experiment_resource['schema'])

        report = validate(os.path.join(temp_dir, 'datapackage.json'))
        self._assert_goodtables(report)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_participant_data_file_info_to_datapackage_json_resources_field(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        participants_resource = next(item for item in json_data['resources'] if item['name'] == 'participants')
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in participants_resource:
            participants_resource.pop('schema')
        test_dict = {
            'name': 'participants', 'title': 'Participants',
            'path': os.path.join('data', 'Participant_data', 'Participants.csv'),
            'format': 'csv', 'mediatype': 'text/csv', 'encoding': 'UTF-8',
            'profile': 'tabular-data-resource'
        }
        self.assertEqual(
            test_dict, participants_resource, str(test_dict) + ' not equal ' + str(participants_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_participants_table_schema_info_to_datapackage_json_participants_resource(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        patient_fields = PATIENT_FIELDS.copy()
        # age field is already included in POST data. Include only the others
        age_field = next(item for item in patient_fields if item['field'] == 'age')
        del patient_fields[patient_fields.index(age_field)]
        # participant_code field is not posted in request
        participant_code_field = next(item for item in patient_fields if item['field'] == 'code')
        del patient_fields[patient_fields.index(participant_code_field)]

        # Append all possible patient attributes in POST data
        for field in patient_fields:
            data['patient_selected'].append(field['field'] + '*' + field['header'])

        # Test for code, full, and abbreviated question texts
        # in Headings head, General information export tab
        for heading_type in ['code'], ['full'], ['abbreviated']:
            data['headings'] = heading_type
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)
            participants_resource = next(item for item in json_data['resources'] if item['name'] == 'participants')

            self.assertIn('schema', participants_resource)
            self.assertIn('fields', participants_resource['schema'])
            self._assert_participants_related_fields_table_schema(
                participants_resource['schema'], heading_type[0], PATIENT_FIELDS)

            report = validate(os.path.join(temp_dir, 'datapackage.json'))
            self.assertTrue(report['valid'])

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_participants_diagnosis_file_info_to_datapackage_json_resources_field(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        data['diagnosis_selected'] = []
        # Append al possible diagnosis attributes in POST data
        for field in DIAGNOSIS_FIELDS:
            data['diagnosis_selected'].append(field['field'] + '*' + field['header'])

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        diagnosis_resource = next(item for item in json_data['resources'] if item['name'] == 'diagnosis')
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in diagnosis_resource:
            diagnosis_resource.pop('schema')

        test_dict = {
            'name': 'diagnosis', 'title': 'Diagnosis',
            'path': os.path.join('data', 'Participant_data', 'Diagnosis.csv'),
            'format': 'csv', 'mediatype': 'text/csv', 'encoding': 'UTF-8',
            'profile': 'tabular-data-resource'
        }
        self.assertEqual(
            test_dict, diagnosis_resource, str(test_dict) + ' not equal ' + str(diagnosis_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_participants_diagnosis_table_schema_info_to_datapackage_json_participants_resource(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        data['diagnosis_selected'] = []
        # Append al possible diagnosis attributes in POST data
        for field in DIAGNOSIS_FIELDS:
            data['diagnosis_selected'].append(field['field'] + '*' + field['header'])

        # Test for code, full and abbreviated question texts
        # in Headings head, General information export tab
        for heading_type in 'code', 'full', 'abbreviated':
            data['headings'] = [heading_type]
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)
            diagnosis_resource = next(item for item in json_data['resources'] if item['name'] == 'diagnosis')
            self.assertIn('schema', diagnosis_resource)
            self.assertIn('fields', diagnosis_resource['schema'])
            self._assert_participants_related_fields_table_schema(
                diagnosis_resource['schema'], heading_type, DIAGNOSIS_FIELDS)

            report = validate(os.path.join(temp_dir, 'datapackage.json'))
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_experimental_protocol_image_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = PROTOCOL_IMAGE_FILENAME.split('.')

        protocol_image_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', PROTOCOL_IMAGE_FILENAME),
            'format': extension, 'mediatype': 'image/png'
        }
        self.assertIn(protocol_image_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_experimental_protocol_description_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data()
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = PROTOCOL_DESCRIPTION_FILENAME.split('.')

        protocol_description_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', PROTOCOL_DESCRIPTION_FILENAME),
            'format': extension, 'mediatype': 'text/txt'
        }
        self.assertIn(protocol_description_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_eeg_default_setting_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = EEG_DEFAULT_SETTING_FILENAME.split('.')

        eeg_default_setting_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', EEG_DEFAULT_SETTING_FILENAME),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(eeg_default_setting_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_eeg_setting_description_file(self):
        self._create_eeg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = EEG_SETTING_FILENAME.split('.')

        eeg_setting_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EEG', 'EEGData_1', EEG_SETTING_FILENAME),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(eeg_setting_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_eeg_data_collection_files(self):
        self._create_eeg_export_data()
        # Adds one more eeg data collection
        eegdata = ObjectsFactory.create_eeg_data(self.dct_eeg, self.subject_of_group, self.eeg_set)
        ObjectsFactory.create_eeg_file(eegdata)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        i = 1  # For EEGData_<str(i)> subdirs
        for eeg_file in EEGFile.objects.order_by('id'):
            filename = os.path.basename(eeg_file.file.name)
            unique_name = slugify(filename)
            file_format_nes_code = eeg_file.eeg_data.file_format.nes_code
            eeg_file_resource = {
                'name': unique_name, 'title': unique_name,
                'path': os.path.join(
                    'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                    'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EEG', 'EEGData_' + str(i), filename),
                'description': 'Data Collection (format: %s)' % file_format_nes_code
            }
            i += 1

            self.assertIn(eeg_file_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_eeg_data_collection_sensor_position_file(self):
        self._create_eeg_export_data()

        # The file saved below is associated with a file format that is considered
        # to generate sensor_postion.png file
        eegdata = EEGData.objects.first()
        eegdata.file_format.nes_code = 'MNE-RawFromEGI'
        eegdata.file_format.save()
        # Get the file uploaded and substitute it by a real EEG raw file
        eegfile = EEGFile.objects.first()
        with File(open('export/tests/example.raw', 'rb')) as f:
            eegfile.file.save('example.raw', f)
        eegfile.save()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = 'sensor_position.png'
        unique_name = slugify(filename)
        eeg_sensor_position_resource = {
            'name': unique_name, 'title': 'sensor_position',
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EEG', 'EEGData_1', filename),
            'description': 'Data Collection (format: png)'
        }

        self.assertIn(eeg_sensor_position_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_eeg_data_collection_nwb_file_resource(self):
        self._create_eeg_export_data()

        # The file saved below is associated with a file format that is considered
        # to generate sensor_postion.png file
        eegdata = EEGData.objects.first()
        eegdata.file_format.nes_code = 'MNE-RawFromEGI'
        eegdata.file_format.save()
        # Create history user for eegdata as nwb creation needs that
        history = eegdata.history.last()
        history.history_user = self.user
        history.save()
        # Get the file uploaded and substitute it by a real EEG raw file
        eegfile = EEGFile.objects.first()
        with File(open('export/tests/example.raw', 'rb')) as f:
            eegfile.file.save('example.raw', f)
        eegfile.save()

        # Create components needed to be able to export raw file to nwb format
        manufacturer = ObjectsFactory.create_manufacturer()
        amplifier = ObjectsFactory.create_amplifier(manufacturer)
        ObjectsFactory.create_eeg_amplifier_setting(self.eeg_set, amplifier)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = 'example.nwb'
        unique_name = slugify(filename)
        nwb_file_resource = {
            'name': unique_name, 'title': 'example',
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EEG', 'EEGData_1', filename),
            'description': 'Data Collection (format: nwb)'
        }

        self.assertIn(nwb_file_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_tms_default_setting_file(self):
        temp_dir = tempfile.mkdtemp()
        self._create_tms_export_data(temp_dir)  # pass temp_dir for hotspot file creation
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_tms_data')

        response = self.client.post(reverse('export_view'), data)

        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = TMS_DEFAULT_SETTING_FILENAME.split('.')
        tms_default_setting_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', TMS_DEFAULT_SETTING_FILENAME),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(tms_default_setting_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_tms_data_description_and_hotspot_map_files(self):
        temp_dir = tempfile.mkdtemp()
        self._create_tms_export_data(temp_dir)  # pass temp_dir for hotspot file creation
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_tms_data')

        response = self.client.post(reverse('export_view'), data)

        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = TMS_DATA_FILENAME.split('.')
        tms_data_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'), 'Per_participant',
                'Participant_' + self.patient.code, 'Step_1_TMS', TMS_DATA_FILENAME),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(tms_data_resource, json_data['resources'])

        filename, extension = HOTSPOT_MAP.split('.')
        hotspot_map_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'), 'Per_participant',
                'Participant_' + self.patient.code, 'Step_1_TMS', HOTSPOT_MAP),
            'format': extension, 'mediatype': 'image/png'
        }
        self.assertIn(hotspot_map_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_emg_default_setting_file(self):
        self._create_emg_export_data()
        self._create_emg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_emg_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = EMG_DEFAULT_SETTING.split('.')

        emg_default_setting_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', EMG_DEFAULT_SETTING),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(emg_default_setting_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_emg_setting_description_file(self):
        self._create_emg_export_data()
        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_emg_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = EMG_SETTING_FILENAME.split('.')

        emg_setting_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'), 'Per_participant',
                'Participant_' + self.patient.code, 'Step_1_EMG', 'EMGData_1', EMG_SETTING_FILENAME),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(emg_setting_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_emg_data_collection_files(self):
        self._create_emg_export_data()
        # Adds one more emg data collection
        emgdata = ObjectsFactory.create_emg_data_collection_data(self.dct_emg, self.subject_of_group, self.emg_set)
        ObjectsFactory.create_emg_data_collection_file(emgdata)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_emg_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        i = 1  # For EMGData_<str(i)> subdirs
        for emg_file in EMGFile.objects.order_by('id'):
            filename = os.path.basename(emg_file.file.name)
            unique_name = slugify(filename)
            file_format_nes_code = emg_file.emg_data.file_format.nes_code
            emg_file_resource = {
                'name': unique_name, 'title': unique_name,
                'path': os.path.join(
                    'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                    'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EMG', 'EMGData_' + str(i), filename),
                'description': 'Data Collection (format: %s)' % file_format_nes_code
            }
            i += 1

            self.assertIn(emg_file_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_goalkeeper_context_tree_default_file(self):
        self._create_goalkeeper_game_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_goalkeeper_game_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        filename, extension = CONTEXT_TREE_DEFAULT.split('.')

        context_tree_resource = {
            'name': filename, 'title': filename,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', CONTEXT_TREE_DEFAULT),
            'format': extension, 'mediatype': 'application/json'
        }
        self.assertIn(context_tree_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_stimulus_file(self):
        # Create a stimulus component
        stimulus_type = ObjectsFactory.create_stimulus_type()
        with tempfile.TemporaryDirectory() as tmpdirname:
            f = ObjectsFactory.create_binary_file(tmpdirname)

            with File(open(f.name, 'rb')) as file:
                stimulus = ObjectsFactory.create_component(
                    self.experiment, Component.STIMULUS,
                    kwargs={'stimulus_type': stimulus_type, 'media_file': file})
        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, stimulus)
        ObjectsFactory.create_data_configuration_tree(component_config)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_stimulus_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        stimulus = Stimulus.objects.first()
        filename = os.path.basename(stimulus.media_file.file.name)
        unique_name = slugify(filename)
        stimulus_resource = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', 'Step_1_STIMULUS', filename),
            'description': 'Stimulus type: %s' % stimulus.stimulus_type.name
        }

        self.assertIn(stimulus_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_generic_data_collection_file(self):
        # Create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION, kwargs={'it': it})

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, gdc)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group)
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_generic_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = os.path.basename(gdcf.file.name)
        unique_name = slugify(filename)
        file_format_nes_code = gdcf.generic_data_collection_data.file_format.nes_code
        gdc_resource = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Per_participant', 'Participant_' + self.patient.code, 'Step_1_GENERIC_DATA_COLLECTION',
                'Generic_Data_Collection_1', filename),
            'description': 'Data Collection (format: %s), information type: %s'
                           % (file_format_nes_code, gdc.information_type.name)
        }

        self.assertIn(gdc_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_goalkeeper_game_files(self):
        digital_game_phase_file = self._create_goalkeeper_game_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_goalkeeper_game_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = os.path.basename(digital_game_phase_file.file.name)
        filename_goalkeeper_game_data_dir = filename.split('_')[0]
        unique_name_filename_goalkeeper_game_data_dir = slugify(filename_goalkeeper_game_data_dir)

        digital_game_phase_resource1 = {
            'name': unique_name_filename_goalkeeper_game_data_dir,
            'title': unique_name_filename_goalkeeper_game_data_dir,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Goalkeeper_game_data', filename_goalkeeper_game_data_dir + '.csv'),
            'encoding': 'UTF-8'
        }

        file_format_nes_code = digital_game_phase_file.digital_game_phase_data.file_format.nes_code
        unique_name = slugify(filename)
        digital_game_phase_resource2 = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'), 'Per_participant',
                'Participant_' + self.patient.code, 'Step_1_DIGITAL_GAME_PHASE', 'DigitalGamePhaseData_1', filename),
            'description': 'Data Collection (format: %s)' % file_format_nes_code
        }

        self.assertIn(digital_game_phase_resource1, json_data['resources'])
        self.assertIn(digital_game_phase_resource2, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_goalkeeper_game_context_tree_file(self):
        self._create_goalkeeper_game_export_data()

        # Add file to context tree setting file
        context_tree = ContextTree.objects.first()
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            with File(open(bin_file.name, 'rb')) as f:
                context_tree.setting_file.save(os.path.basename(bin_file.name), f)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_goalkeeper_game_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = os.path.basename(context_tree.setting_file.name)
        unique_name = slugify(filename)
        dgp_settingfile_resource = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', filename),
            'description': 'Context tree setting file'
        }

        self.assertIn(dgp_settingfile_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_experimental_protocol_additional_file(self):
        # TODO (NES-991): by now, additional data from Experimental Protocol (set of steps) appears to have not being
        #  exported
        pass
        # Create a file and add it as an additional file of the root component
        # with tempfile.TemporaryDirectory() as tmpdirname:
        #     with open(os.path.join(tmpdirname, 'stepadditionaldata.bin'), 'wb') as f:
        #         f.write(b'carambola')
        #         with File(open(f.name, 'rb')) as file:
        #             additional_file = ComponentAdditionalFile.objects.create(component=self.root_component, file=file)
        #
        # self.append_session_variable('group_selected_list', [str(self.group.id)])
        # self.append_session_variable('license', '0')
        #
        # data = self._set_post_data('per_additional_data')
        #
        # response = self.client.post(reverse('export_view'), data)
        #
        # temp_dir = tempfile.mkdtemp()
        # json_data = self.get_datapackage_json_data(temp_dir, response)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_step_additional_file(self):
        # Create generic data collection (gdc) component, it could been any data collection
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(self.experiment, Component.GENERIC_DATA_COLLECTION, kwargs={'it': it})

        # Create a file and add it as an additional file of the step
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'stepadditionaldata.bin'), 'wb') as f:
                f.write(b'carambola')
                with File(open(f.name, 'rb')) as file:
                    additional_file = ComponentAdditionalFile.objects.create(component=gdc, file=file)

        # Include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(self.root_component, gdc)
        ObjectsFactory.create_data_configuration_tree(component_config)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_generic_data')

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = os.path.basename(additional_file.file.name)
        unique_name = slugify(filename)

        additional_data_resource = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Experimental_protocol', 'Step_1_GENERIC_DATA_COLLECTION', 'AdditionalData', filename
            ),
            'description': 'Step additional file'
        }
        self.assertIn(additional_data_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_per_experiment_adds_participant_data_collection_additional_file(self):
        self._create_eeg_export_data()
        additional_data = ObjectsFactory.create_additional_data_data(self.dct_eeg, self.subject_of_group)
        additional_file = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = os.path.basename(additional_file.file.name)
        unique_name = slugify(filename)
        file_format_nes_code = additional_file.additional_data.file_format.nes_code
        additional_data_resource = {
            'name': unique_name, 'title': unique_name,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Per_participant', 'Participant_' + self.patient.code, 'Step_1_EEG',
                'AdditionalData_1', filename),
            'description': 'Data Collection (additional file, format: %s)' % file_format_nes_code
        }

        self.assertIn(additional_data_resource, json_data['resources'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_metadata_file_to_datapackage_json_file(self, mockServer):
        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        set_mocks6(mockServer)
        data = {
            'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*Textfrage*Textfrage',
                ],
            'patient_selected': ['age*age'], 'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        code = self.questionnaire.survey.code
        filename = 'Fields_' + code + '_en.csv'
        unique_name = slugify('Fields_' + code)
        title = 'Fields_' + code

        questionnaire_metadata_resource = next(
            item for item in json_data['resources'] if item['title'] == 'Fields_' + code)
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in questionnaire_metadata_resource:
            questionnaire_metadata_resource.pop('schema')
        test_dict = {
            'name': unique_name, 'title': title,
            'path': os.path.join(
                'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                'Questionnaire_metadata', code + '_' + slugify(self.questionnaire.survey.en_title), filename),
            'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire metadata',
            'profile': 'tabular-data-resource',
        }
        self.assertEqual(
            test_dict, questionnaire_metadata_resource,
            str(test_dict) + ' not equal ' + str(questionnaire_metadata_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_metadata_table_schema_info_to_questionnaire_metadata_resource(
            self, mockServer):
        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        set_mocks6(mockServer)
        data = {
            'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*Textfrage*Textfrage',
                ],
            'patient_selected': ['age*age'], 'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        code = self.questionnaire.survey.code
        questionnaire_metadata_resource = next(
            item for item in json_data['resources'] if item['title'] == 'Fields_' + code)

        for item in HEADER_EXPLANATION_FIELDS:
            self.assertIn(
                {'name': item[0], 'title': item[0], 'type': item[1], 'format': 'default'},
                questionnaire_metadata_resource['schema']['fields'])

        report = validate(os.path.join(temp_dir, 'datapackage.json'))
        self._assert_goodtables(report)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_responses_file_to_datapackage_json_file1(self, mockServer):
        """In Per_questionnaire subdir"""
        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks6(mockServer)
            if heading_type == 'full':
                update_mocks6_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks6_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to_experiment[]': [
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                    + '*' + self.questionnaire.survey.en_title + '*acquisitiondate*acquisitiondate',
                    '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                    + '*' + self.questionnaire.survey.en_title + '*Textfrage*Textfrage',
                ],
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = self.survey.code + '_' + slugify(self.survey.en_title) + '_en'
            extension = '.csv'

            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': slugify(filename), 'title': filename,
                'path': os.path.join(
                    'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                    'Per_questionnaire', 'Step_1_QUESTIONNAIRE', filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                'Failed for heading type ' + "'" + heading_type + "'\n"
                + str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_responses_file_to_datapackage_json_file2(self, mockServer):
        """In Per_participant subdir"""

        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to_experiment = []
        for question in questions:
            to_experiment.append(
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks7(mockServer)
            if heading_type == 'full':
                update_mocks7_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks7_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to_experiment[]': to_experiment,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = self.survey.code + '_' + slugify(self.survey.en_title) + '_en'
            extension = '.csv'
            unique_name = slugify(filename) + '_per-participant'

            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['name'] == unique_name)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': unique_name, 'title': filename,
                'path': os.path.join(
                    'data', 'Experiment_data', 'Group_' + slugify(self.group.title).replace('-', '_'),
                    'Per_participant', 'Participant_' + self.patient.code, 'Step_1_QUESTIONNAIRE', filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_responses_table_schema_info_to_datapackage_json_file1(
            self, mockServer):
        """In Per_questionnaire subdir"""

        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to_experiment = []
        for question in questions:
            to_experiment.append(
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks7(mockServer)
            if heading_type == 'full':
                update_mocks7_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks7_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to_experiment[]': to_experiment,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = self.survey.code + '_' + slugify(self.survey.en_title) + '_en'
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'],
                    'Failed for heading type ' + "'" + heading_type + "'")

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_questionnaire_responses_table_schema_info_to_datapackage_json_file2(
            self, mockServer):
        """In Per_participant subdir"""

        self._create_questionnaire_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to_experiment = []
        for question in questions:
            to_experiment.append(
                '0*' + str(self.group.id) + '*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks7(mockServer)
            if heading_type == 'full':
                update_mocks7_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks7_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to_experiment[]': to_experiment,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = self.survey.code + '_' + slugify(self.survey.en_title) + '_en'
            unique_name = slugify(filename) + '_per-participant'
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['name'] == unique_name)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'])

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_metadata_file_to_datapackage_json_file(self, mockServer):
        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        set_mocks11(mockServer)
        data = {
            'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
            'headings': ['code'],
            'to[]': to,
            'patient_selected': ['age*age'], 'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = 'Fields_' + str(self.survey.lime_survey_id) + '_en'
        extension = '.csv'

        questionnaire_response_resource = next(
            item for item in json_data['resources'] if item['title'] == filename)
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in questionnaire_response_resource:
            questionnaire_response_resource.pop('schema')
        test_dict = {
            'name': slugify(filename), 'title': filename,
            'path': os.path.join(
                'data', 'Participant_data', 'Questionnaire_metadata',
                str(self.survey.lime_survey_id) + '_' + slugify(self.survey.en_title), filename + extension),
            'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire metadata',
            'profile': 'tabular-data-resource'
        }
        self.assertEqual(
            test_dict, questionnaire_response_resource,
            str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_metadata_table_schema_info_to_datapackage(
            self, mockServer):
        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        set_mocks11(mockServer)
        data = {
            'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
            'headings': ['code'],
            'to[]': to,
            'patient_selected': ['age*age'], 'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        filename = 'Fields_' + str(self.survey.lime_survey_id) + '_en'
        questionnaire_response_resource = next(
            item for item in json_data['resources'] if item['title'] == filename)
        for item in HEADER_EXPLANATION_FIELDS:
            self.assertIn(
                {
                    'name': item[0], 'title': item[0], 'type': item[1], 'format': 'default'
                }, questionnaire_response_resource['schema']['fields'])

        report = validate(os.path.join(temp_dir, 'datapackage.json'), skip_checks=['duplicate-row'])
        self._assert_goodtables(report)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_responses_file_to_datapackage_json_file1(
            self, mockServer):
        """In Per_questionnaire subdir"""
        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks11(mockServer)
            if heading_type == 'full':
                update_mocks11_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks11_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to[]': to,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + str(self.survey.lime_survey_id) + '_en'
            extension = '.csv'

            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': slugify(filename), 'title': filename,
                'path': os.path.join(
                    'data', 'Participant_data', 'Per_questionnaire',
                    str(self.survey.lime_survey_id) + '_' + slugify(self.survey.en_title),
                    filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                'Failed for heading type ' + "'" + heading_type + "'\n"
                + str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_responses_file_to_datapackage_json_file2(
            self, mockServer):
        """In Per_participant subdir"""

        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks11(mockServer)
            if heading_type == 'full':
                update_mocks11_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks11_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'action': ['run'], 'per_questionnaire': ['on'],
                'headings': [heading_type],
                'to[]': to,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + str(self.survey.code) + '_en'
            extension = '.csv'

            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': slugify(filename), 'title': filename,
                'path': os.path.join(
                    'data', 'Participant_data', 'Per_participant', 'Participant_' + self.patient.code,
                    self.survey.code + '_' + slugify(self.survey.en_title), filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                'Failed for heading type ' + "'" + heading_type + "'\n"
                + str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_responses_table_schema_info_to_datapackage1(
            self, mockServer):
        """In Per_questionnaire subdir"""
        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks11(mockServer)
            if heading_type == 'full':
                update_mocks11_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks11_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'per_questionnaire': ['on'], 'action': ['run'],
                'headings': [heading_type],
                'to[]': to,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + str(self.survey.lime_survey_id) + '_en'
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'])

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_experiment_adds_entrance_questionnaire_responses_table_schema_info_to_datapackage2(
            self, mockServer):
        """In Per_participant subdir"""

        self._create_questionnaire_export_data()
        UtilTests.create_response_survey(self.user, self.patient, self.survey, token_id=1)

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        questions = self._set_all_questions()

        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1)
                + '*' + self.questionnaire.survey.en_title + '*' + question[0]['code'] + '*' + question[0]['code'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks11(mockServer)
            if heading_type == 'full':
                update_mocks11_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks11_abbreviated(mockServer)
            data = {
                'per_participant': ['on'], 'per_questionnaire': ['on'], 'action': ['run'],
                'headings': [heading_type],
                'to[]': to,
                'patient_selected': ['age*age'], 'responses': ['short']
            }
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + str(self.survey.code) + '_en'
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'])

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_creates_datapackage_json_file(self, mockServer):
        survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        UtilTests.create_response_survey(self.user, self.patient, survey, token_id=1)
        set_mocks10(mockServer)

        questions = self._set_all_questions()
        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey.en_title + '*' + question[0]['code']
                + '*' + question[0]['code'])

        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)
        self.assertTrue(any('datapackage.json' in element for element in zipped_file.namelist()),
                        'datapackage.json not found in: ' + str(zipped_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_basic_content_to_datapackage_json_file(self, mockServer):
        survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        UtilTests.create_response_survey(self.user, self.patient, survey, token_id=1)
        set_mocks10(mockServer)

        questions = self._set_all_questions()
        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey.en_title + '*' + question[0]['code']
                + '*' + question[0]['code'])

        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        self._assert_basic_per_participant_data(json_data)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaires_contributors_to_datapackage_json_file(self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        # Values from mocks
        contributor1 = 'Jorge da Capadócia'
        contributor1_email = 'jorge@example.com'
        contributor2 = 'Leonardo dos Santos'
        contributor2_email = 'leo@example.com'

        self.assertIn('contributors', json_data)
        self.assertIn(
            {
                'title': contributor1, 'email': contributor1_email,
                'questionnaire': str(LIMESURVEY_SURVEY_ID_1) + ' - ' + survey1.en_title
            },
            json_data['contributors'])
        self.assertIn(
            {
                'title': contributor2, 'email': contributor2_email,
                'questionnaire': str(LIMESURVEY_SURVEY_ID_2) + ' - ' + survey2.en_title
            },
            json_data['contributors'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_displays_license_options_in_form_with_default_to_creative_commons(self, mockServer):
        survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        UtilTests.create_response_survey(self.user, self.patient, survey, token_id=1)
        set_mocks8(mockServer)

        # Needed because if session expired this variable does not exist in request.session
        # anymore. See the view.
        self.append_session_variable('filtered_participant_data', [self.patient.id])
        
        response = self.client.get(reverse('export_view'))

        self.assertIn(str(_('License')), response.content.decode('utf-8'))
        self.assertIn('Creative Commons', response.content.decode('utf-8'))
        self.assertIn('Copyright', response.content.decode('utf-8'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_default_license_to_datapackage_json_file(self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('licenses', json_data)
        self.assertIn({
            'name': 'CC', 'path': 'https://creativecommons.org', 'title': 'Creative Commons'
        }, json_data['licenses'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_creative_commons_license_to_datapackage_json_file(self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '1',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        self.assertIn('licenses', json_data)
        self.assertIn({
            'name': '©', 'path': 'https://simple.wikipedia.org/wiki/Copyright', 'title': 'Copyright'
        }, json_data['licenses'])

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_participant_data_file_info_to_datapackage_json_resources_field(
            self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        participants_resource = next(item for item in json_data['resources'] if item['name'] == 'participants')
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in participants_resource:
            participants_resource.pop('schema')

        test_dict = {
            'name': 'participants', 'title': 'Participants',
            'path': os.path.join('data', 'Participants.csv'),
            'format': 'csv', 'mediatype': 'text/csv', 'encoding': 'UTF-8',
            'profile': 'tabular-data-resource',
        }
        self.assertEqual(
            test_dict, participants_resource, str(test_dict) + ' not equal ' + str(participants_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_participants_table_schema_info_to_datapackage_json_participants_resource(
            self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'license': '0', 'to[]': to
        }
        patient_fields = PATIENT_FIELDS.copy()
        # participant_code field is included besides PATIENT_FIELDS
        participant_code = next(item for item in patient_fields if item['field'] == 'code')
        del (patient_fields[patient_fields.index(participant_code)])
        # Append all possible patient attributes in POST data
        data['patient_selected'] = []
        for field in patient_fields:
            data['patient_selected'].append(field['field'] + '*' + field['header'])

        # Test for code, full, and abbreviated question texts
        # in Headings head, General information export tab
        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks9(mockServer)
            if heading_type == 'full':
                update_mocks9_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks9_abbreviated(mockServer)
            data['headings'] = heading_type
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)
            participants_resource = next(item for item in json_data['resources'] if item['name'] == 'participants')

            self.assertIn('schema', participants_resource)
            self.assertIn('fields', participants_resource['schema'])
            self._assert_participants_related_fields_table_schema(
                participants_resource['schema'], heading_type, PATIENT_FIELDS)

            report = validate(os.path.join(temp_dir, 'datapackage.json'))
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_participants_diagnosis_file_info_to_datapackage_json_resources_field(
            self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'], 'files_format': ['csv'],
            'action': ['run'], 'responses': ['short'], 'patient_selected': ['age*age'], 'license': '0', 'to[]': to,
            'diagnosis_selected': []
        }
        # Append al possible diagnosis attributes in POST data
        for field in DIAGNOSIS_FIELDS:
            data['diagnosis_selected'].append(field['field'] + '*' + field['header'])

        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)
        diagnosis_resource = next(item for item in json_data['resources'] if item['name'] == 'diagnosis')
        # Remove schema field if it exists. The test was written before the
        # test that drives adding schema field to datapackage.json
        if 'schema' in diagnosis_resource:
            diagnosis_resource.pop('schema')

        test_dict = {
            'name': 'diagnosis', 'title': 'Diagnosis',
            'path': os.path.join('data', 'Diagnosis.csv'),
            'format': 'csv', 'mediatype': 'text/csv', 'encoding': 'UTF-8',
            'profile': 'tabular-data-resource',
        }
        self.assertEqual(
            test_dict, diagnosis_resource, str(test_dict) + ' not equal ' + str(diagnosis_resource))

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_participants_diagnosis_table_schema_info_to_datapackage_json_participants_resource(
            self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'per_participant': ['on'], 'per_questionnaire': ['on'], 'files_format': ['csv'],
            'action': ['run'], 'responses': ['short'], 'patient_selected': ['age*age'], 'license': '0', 'to[]': to,
            'diagnosis_selected': []
        }
        # Append all possible diagnosis attributes in POST data
        for field in DIAGNOSIS_FIELDS:
            data['diagnosis_selected'].append(field['field'] + '*' + field['header'])

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks9(mockServer)
            if heading_type == 'full':
                update_mocks9_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks9_abbreviated(mockServer)
            data['headings'] = heading_type
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)
            diagnosis_resource = next(item for item in json_data['resources'] if item['name'] == 'diagnosis')
            self.assertIn('schema', diagnosis_resource)
            self.assertIn('fields', diagnosis_resource['schema'])
            self._assert_participants_related_fields_table_schema(
                diagnosis_resource['schema'], heading_type, DIAGNOSIS_FIELDS)

            report = validate(os.path.join(temp_dir, 'datapackage.json'))
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_metadata_file_to_datapackage_json_file(self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        for survey in [survey1, survey2]:
            filename = 'Fields_' + str(survey.lime_survey_id) + '_en.csv'
            unique_name = slugify('Fields_' + str(survey.lime_survey_id) + '_' + 'en')
            title = 'Fields_' + str(survey.lime_survey_id) + '_' + 'en'

            questionnaire_metadata_resource = next(item for item in json_data['resources'] if item['title'] == title)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_metadata_resource:
                questionnaire_metadata_resource.pop('schema')
            test_dict = {
                'name': unique_name, 'title': title,
                'path': os.path.join(
                    'data', 'Questionnaire_metadata',
                    str(survey.lime_survey_id) + '_' + slugify(survey.en_title), filename),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire metadata',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_metadata_resource,
                str(test_dict) + ' not equal ' + str(questionnaire_metadata_resource)
            )

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_metadata_table_schema_to_questionnaire_metadata_resource(
            self, mockServer):
        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        for survey in [survey1, survey2]:
            title = 'Fields_' + str(survey.lime_survey_id) + '_' + 'en'
            questionnaire_metadata_resource = next(item for item in json_data['resources'] if item['title'] == title)

            for item in HEADER_EXPLANATION_FIELDS:
                self.assertIn(
                    {'name': item[0], 'title': item[0], 'type': item[1], 'format': 'default'},
                    questionnaire_metadata_resource['schema']['fields'])

        report = validate(os.path.join(temp_dir, 'datapackage.json'))
        self._assert_goodtables(report)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_response_file_to_datapackage_json_file1(self, mockServer):
        """In Per_questionnaire subdir"""

        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        for survey in [survey1, survey2]:
            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + slugify(survey.lime_survey_id) + '_en'
            extension = '.csv'

            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': slugify(filename), 'title': filename,
                'path': os.path.join(
                    'data', 'Per_questionnaire',
                    str(survey.lime_survey_id) + '_' + slugify(survey.en_title),
                    filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_responses_table_schema_info_to_datapackage1(self, mockServer):
        """In Per_questionnaire subdir"""

        survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        UtilTests.create_response_survey(self.user, self.patient, survey, token_id=1)

        questions = self._set_all_questions()
        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey.en_title + '*' + question[0]['code']
                + '*' + question[0]['code'])

        patient_selected = [
            'age*age',
            'socialdemographicdata__patient_schooling__name*patient_schooling'
        ]
        data = {
            'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': patient_selected, 'license': '0', 'to[]': to
        }
        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks10(mockServer)
            if heading_type == 'full':
                update_mocks10_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks10_abbreviated(mockServer)
            data['headings'] = [heading_type]
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + slugify(survey.lime_survey_id) + '_en'
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['title'] == filename)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'])
            for patient_field_selected in patient_selected:
                patient_field_selected = patient_field_selected.split('*')[0]
                patient_field = next(item for item in PATIENT_FIELDS if item['field'] == patient_field_selected)
                title = ''
                if heading_type == 'code':
                    title = patient_field['header']
                elif heading_type == 'full':
                    title = patient_field['description']
                elif heading_type == 'abbreviated':
                    title = abbreviated_data(patient_field['description'])
                self.assertIn(
                    {
                        'name': title, 'title': title, 'type': patient_field['json_data_type'],
                        'format': 'default'
                    }, questionnaire_response_resource['schema']['fields']
                )

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_response_file_to_datapackage_json_file2(self, mockServer):
        """In Per_participant subdir"""

        # It's important to keep the order: first 'Q5050' then 'Q2121'.
        # See comment in export.process_per_participant method
        survey1 = create_survey(LIMESURVEY_SURVEY_ID_1)
        survey1.code = 'Q5050'
        survey1.save()
        UtilTests.create_response_survey(self.user, self.patient, survey1, token_id=1)
        survey2 = create_survey(LIMESURVEY_SURVEY_ID_2)
        survey2.code = 'Q2121'
        survey2.save()
        UtilTests.create_response_survey(self.user, self.patient, survey2, token_id=1)
        set_mocks9(mockServer)

        to = [
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*acquisitiondate*acquisitiondate',
            '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey1.en_title + '*textfrageeins*textfrageeins',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*acquisitiondate*acquisitiondate',
            '1*' + str(LIMESURVEY_SURVEY_ID_2) + '*' + survey2.en_title + '*textfragezwei*textfragezwei'
        ]
        data = {
            'headings': ['code'], 'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': ['age*age'], 'license': '0',
            'to[]': to
        }
        response = self.client.post(reverse('export_view'), data)

        for survey in [survey1, survey2]:
            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + survey.code + '_en'
            extension = '.csv'

            path_resource = os.path.join(
                'data', 'Per_participant', 'Participant_' + self.patient.code,
                survey.code + '_' + slugify(survey.en_title), filename + extension)
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['path'] == path_resource)
            # Remove schema field if it exists. The test was written before the
            # test that drives adding schema field to datapackage.json
            if 'schema' in questionnaire_response_resource:
                questionnaire_response_resource.pop('schema')
            test_dict = {
                'name': slugify(filename), 'title': filename,
                'path': os.path.join(
                    'data', 'Per_participant', 'Participant_' + self.patient.code,
                    str(survey.code) + '_' + slugify(survey.en_title), filename + extension),
                'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                'profile': 'tabular-data-resource',
            }
            self.assertEqual(
                test_dict, questionnaire_response_resource,
                str(test_dict) + ' not equal ' + str(questionnaire_response_resource))

            shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_per_participant_adds_questionnaire_responses_table_schema_info_to_datapackage2(self, mockServer):
        """In Per_participant subdir"""

        survey = create_survey(LIMESURVEY_SURVEY_ID_1)
        UtilTests.create_response_survey(self.user, self.patient, survey, token_id=1)

        questions = self._set_all_questions()
        to = []
        for question in questions:
            to.append(
                '0*' + str(LIMESURVEY_SURVEY_ID_1) + '*' + survey.en_title + '*' + question[0]['code']
                + '*' + question[0]['code'])

        patient_selected = [
            'age*age',
            'socialdemographicdata__patient_schooling__name*patient_schooling'
        ]
        data = {
            'per_participant': ['on'], 'per_questionnaire': ['on'],
            'files_format': ['csv'], 'action': ['run'], 'responses': ['short'],
            'patient_selected': patient_selected, 'license': '0', 'to[]': to
        }

        for heading_type in 'code', 'full', 'abbreviated':
            set_mocks10(mockServer)
            if heading_type == 'full':
                update_mocks10_full(mockServer)
            if heading_type == 'abbreviated':
                update_mocks10_abbreviated(mockServer)
            data['headings'] = [heading_type]
            response = self.client.post(reverse('export_view'), data)

            temp_dir = tempfile.mkdtemp()
            json_data = self.get_datapackage_json_data(temp_dir, response)

            filename = 'Responses_' + survey.code + '_en'
            extension = '.csv'
            path_resource = os.path.join(
                'data', 'Per_participant', 'Participant_' + self.patient.code,
                survey.code + '_' + slugify(survey.en_title), filename + extension)
            questionnaire_response_resource = next(
                item for item in json_data['resources'] if item['path'] == path_resource)
            for item in questions:
                self.assertIn(
                    {
                        'name': item[0][heading_type], 'title': item[0][heading_type], 'type': item[2],
                        'format': item[3]
                    }, questionnaire_response_resource['schema']['fields'])
            for patient_field_selected in patient_selected:
                patient_field_selected = patient_field_selected.split('*')[0]
                patient_field = next(item for item in PATIENT_FIELDS if item['field'] == patient_field_selected)
                title = ''
                if heading_type == 'code':
                    title = patient_field['header']
                elif heading_type == 'full':
                    title = patient_field['description']
                elif heading_type == 'abbreviated':
                    title = abbreviated_data(patient_field['description'])
                self.assertIn(
                    {
                        'name': title, 'title': title, 'type': patient_field['json_data_type'],
                        'format': 'default'
                    }, questionnaire_response_resource['schema']['fields']
                )

            report = self._set_validation_for_goodtables(os.path.join(temp_dir, 'datapackage.json'), heading_type)
            self._assert_goodtables(report)

            shutil.rmtree(temp_dir)

    def test_export_adds_resource_has_already_resource_with_same_name_adds_hash(self):
        # eeg file and emg file are going to have the same name: file.bin
        self._create_eeg_export_data()
        self._create_emg_export_data()

        self.append_session_variable('group_selected_list', [str(self.group.id)])
        self.append_session_variable('license', '0')

        data = self._set_post_data('per_eeg_raw_data', 'per_emg_data')
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        json_data = self.get_datapackage_json_data(temp_dir, response)

        eeg_emg_resources = [
            resource for resource in json_data['resources']
            if 'file' in os.path.basename(resource['path'])
        ]

        self.assertNotEqual(eeg_emg_resources[0]['name'], eeg_emg_resources[1]['name'])

        shutil.rmtree(temp_dir)


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT)
