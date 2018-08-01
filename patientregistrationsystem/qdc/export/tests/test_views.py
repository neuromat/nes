import os
import io
import zipfile
from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from experiment.models import Component, Subject, SubjectOfGroup
from experiment.tests_original import ObjectsFactory
from patient.tests import UtilTests
from qdc import settings
from survey.abc_search_engine import Questionnaires
from survey.models import Survey


class ExportQuestionnaireTest(TestCase):

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
        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        # self.assertTrue(self.user.is_authenticated())  # DEBUG
        # self.assertIn('_auth_user_id', self.client.session)  # DEBUG

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
        subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=self.group
        )
        self.group.subjectofgroup_set.add(subject_of_group)

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

        # create other group and questions
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
            subject_of_group=subject_of_group
        )

    def tearDown(self):
        self.lime_survey.delete_survey(self.sid)
        self.client.logout()

    def test_same_questionnaire_used_in_different_steps_return_correct_content(self):
        # TODO: testar com sobreposição do subdiretório media

        # create other subject of group
        patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = Subject.objects.create(patient=patient)
        subject_of_group = SubjectOfGroup.objects.create(
            subject=subject, group=self.group
        )
        self.group.subjectofgroup_set.add(subject_of_group)

        # create other component QUESTIONNAIRE in same experimental protocol
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

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

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

        for element in zipped_file.namelist():  # DEBUG
            print(element)  # DEBUG
