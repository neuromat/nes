# -*- coding: UTF-8 -*-

import os
import sys
import tempfile

from datetime import date, datetime

from xml.etree.ElementTree import XML
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.messages.api import MessageFailure
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from faker import Factory

from experiment.models import Experiment, Group, Subject, \
    QuestionnaireResponse as ExperimentQuestionnaireResponse, SubjectOfGroup, ComponentConfiguration, ResearchProject, \
    Questionnaire, Block, DataConfigurationTree

from patient.management.commands.import_icd import import_classification_of_diseases
from patient.models import ClassificationOfDiseases, MedicalRecordData, Diagnosis, ComplementaryExam, ExamFile, \
    Gender, Schooling, Patient, AlcoholFrequency, AlcoholPeriod, AmountCigarettes, QuestionnaireResponse, Telephone, \
    MaritalStatus
from patient.views import medical_record_view, medical_record_update, diagnosis_create, \
    medical_record_create_diagnosis_create, exam_create, exam_view, \
    patient_update, patient_view, restore_patient, reverse, check_limesurvey_access
from patient.validation import CPF

from survey.abc_search_engine import Questionnaires
from survey.models import Survey

from update_english_data import translate_fixtures_into_english, update_translated_data

# Constants para testes de User
USER_EDIT = 'user_edit'
USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
USER_NEW = 'user_new'

# Constantes para testes participante
ACTION = 'action'
CPF_ID = 'cpf'
SEARCH_TEXT = 'search_text'

PATIENT_SEARCH = 'patient_search'
PATIENT_VIEW = 'patient_view'
PATIENT_NEW = 'patient_new'
PATIENT_EDIT = 'patient_edit'
QUESTIONNAIRE_NEW = 'questionnaire_response_create'
QUESTIONNAIRE_EDIT = 'questionnaire_response_edit'
QUESTIONNAIRE_VIEW = 'questionnaire_response_view'

# questionnaire incomplete (CLEAN_QUESTIONNAIRE)
CLEAN_QUESTIONNAIRE = 247189
# questionnaire completed filled (FILLED_QUESTIONNAIRE)
FILLED_QUESTIONNAIRE = 0
# questionnaire with error: tokens table not started (NO_TOKEN_TABLE)
NO_TOKEN_TABLE = 0
# questionnaire with error: questionnaire not activated
QUESTIONNAIRE_NOT_ACTIVE = 0
# questionnaire with error: missing standard fields
MISSING_STANDARD_FIEDS = 0
TOKEN_NOT_GENERATED = 0  # questionnaire with error: token not generated
SURVEY_INVALID = 0  # questionnaire with error: invalid survey
LIME_SURVEY_TOKEN_ID_1 = 1


class UtilTests:

    @staticmethod
    # TODO: changed_by can't be None, changed_by is required!
    def create_patient(name='Patient Test', changed_by=None):
        """Cria um participante para ser utilizado durante os testes"""
        faker = Factory.create()

        # TODO:
        # create gender before create patient in other helper method
        try:
            gender = Gender.objects.get(name='Masculino')
        except ObjectDoesNotExist:
            gender = Gender.objects.create(name='Masculino')

        # TODO: make loop to guarantee unique patient cpf
        return Patient.objects.create(
            name=name, date_birth=faker.date(), cpf=faker.ssn(), gender=gender, changed_by=changed_by,
            marital_status=MaritalStatus.objects.create(name=faker.word())
        )

    @staticmethod
    def create_telephone(patient, changed_by):
        return Telephone.objects.create(
            patient=patient, number='9 9999 9999', type=Telephone.MOBILE, changed_by=changed_by
        )

    @staticmethod
    def create_cid10_to_search():
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()
        cid10 = ClassificationOfDiseases.objects.create(code='B01', description='Febres tifoide ',
                                                        abbreviated_description='B01 Febres tifoide ')
        cid10.save()

    @staticmethod
    def create_cid10(code=None):
        """Create classification of desease"""
        faker = Factory.create()

        code = code if code is not None else 'A01'
        return ClassificationOfDiseases.objects.create(
            code=code, description=faker.sentence(nb_words=10), abbreviated_description=faker.sentence(nb_words=6)
        )

    @staticmethod
    def create_medical_record(user, patient):
        return MedicalRecordData.objects.create(patient=patient, record_responsible=user)

    @staticmethod
    def create_diagnosis(medical_record, cid10=None):
        if cid10 is None:
            cid10 = UtilTests.create_cid10()
        return Diagnosis.objects.create(
            medical_record_data=medical_record, classification_of_diseases=cid10
        )

    @staticmethod
    def create_survey_mock(survey_id, is_initial_evaluation):
        survey = Survey(lime_survey_id=survey_id, is_initial_evaluation=is_initial_evaluation)
        survey.save()

        return survey

    @staticmethod
    def create_token_id_mock(survey):
        questionnaire_lime_survey = Questionnaires()
        result = \
            questionnaire_lime_survey.add_participant(survey.lime_survey_id)
        questionnaire_lime_survey.release_session_key()

        return result['tid']

    @staticmethod
    def create_limesurvey_participant(survey, lime_survey):
        result = \
            lime_survey.add_participant(survey.lime_survey_id)

        return result

    @staticmethod
    def create_response_survey_mock(responsible, patient, survey, token_id=None):
        if not token_id:
            token_id = UtilTests.create_token_id_mock(survey)

        return QuestionnaireResponse.objects.create(
            patient=patient, survey=survey, token_id=token_id,
            questionnaire_responsible=responsible
        )


class CpfValidationTest(TestCase):
    good_values = (
        '288.666.827-30',
        '597.923.110-25',
        '981.108.954-09',
        '174.687.414-76',
        '774.321.431-10',
    )

    good_only_numbers_values = (
        '28866682730',
        '59792311025',
        '98110895409',
        '17468741476',
        '77432143110',
    )

    bad_values = (
        '288.666.827-31',
        '597.923.110-26',
        '981.108.954-00',
        '174.687.414-77',
        '774.321.431-11',
    )

    bad_only_numbers_values = (
        '28866682731',
        '59792311026',
        '98110895400',
        '17468741477',
        '77432143111',
    )

    invalid_values = (
        '00000000000',
        '11111111111',
        '22222222222',
        '33333333333',
        '44444444444',
        '55555555555',
        '66666666666',
        '77777777777',
        '88888888888',
        '99999999999'
    )

    def test_good_values(self):
        """testa os valores validos"""
        for cpf in self.good_values:
            result = CPF(cpf).isValid()
            self.assertEqual(result, True)

    def test_good_only_numbers_values(self):
        """testa os valores validos para somente numeros"""
        for cpf in self.good_only_numbers_values:
            result = CPF(cpf).isValid()
            self.assertEqual(result, True)

    def test_bad_values(self):
        """testa os valores invalidos"""
        for cpf in self.bad_values:
            result = CPF(cpf).isValid()
            self.assertEqual(result, False)

    def test_bad_only_numbers_values(self):
        """testa os valores invalidos para somente numeros"""
        for cpf in self.bad_only_numbers_values:
            result = CPF(cpf).isValid()
            self.assertEqual(result, False)

    def test_empty_value(self):
        """testa cpf vazio """
        result = CPF('').isValid()
        self.assertEqual(result, False)

    def test_alpha_value(self):
        """testa cpf com letras"""
        result = CPF('111.ABC').isValid()
        self.assertEqual(result, False)

    def test_special_character_value(self):
        """testa cpf com letras"""
        result = CPF('!@#$%&*()-_=+[]|"?><;:').isValid()
        self.assertEqual(result, False)

    def test_long_string_value(self):
        """testa cpf com letras"""
        result = CPF(
            '1234567890123456789012345678901234567890123456789012\
            34567890123456789012345678901234567890123456789012345678901234567890').isValid()
        self.assertEqual(result, False)

    def test_invalid_values(self):
        """testa os valores invalidos por conter somente digitos repetidos"""
        for cpf in self.invalid_values:
            result = CPF(cpf).isValid()
            self.assertEqual(result, False)


class PatientFormValidation(TestCase):
    user = ''
    data = {}
    util = UtilTests()

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        # print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.gender = Gender.objects.create(name='Masculino')
        self.gender.save()

        self.data = {'name': 'Patient for test',
                     'cpf': '374.276.738-08',
                     'gender': str(self.gender.id),
                     'date_birth': '01/02/1995',
                     'email': 'email@email.com'}

    def test_patient_invalid_cpf(self):
        """
        Testa inclusao de participante com cpf invalido
        """

        # CPF invalido
        cpf = '100.913.651-81'
        self.data['cpf'] = cpf

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf", 'CPF ' + cpf + _(' is not valid'))

    def test_patient_empty_cpf(self):
        """
        Tests inclusion of participant with invalid (empty) cpf
        """

        # Empty CPF
        name = self._testMethodName
        self.data['name'] = name
        self.data[CPF_ID] = ''

        # This data is required for the ManagementForm. This form is used by
        # the formset to manage the collection of forms contained in the
        # formset.
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def test_patient_future_date_birth(self):
        """
        Testa inclusao de participante com data de nascimento futura
        """
        name = self._testMethodName
        self.data['name'] = name
        self.data['date_birth'] = '15/05/2201'

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name=name).count(), 0)

    def get_current_date(self):
        """
        Obtem a data atual no formato dd/mm/yyyy
        """
        d = date.today()
        d.isoformat()
        date_birth = d.strftime("%d/%m/%Y")
        return date_birth

    def test_patient_date_birth_now(self):
        """
        Testa inclusao de participante com data de nascimento futura
        """

        date_birth = self.get_current_date()
        name = self._testMethodName
        self.data['date_birth'] = date_birth
        self.data['name'] = name

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def fill_management_form(self):
        self.data['telephone_set-TOTAL_FORMS'] = '3'
        self.data['telephone_set-INITIAL_FORMS'] = '0'
        self.data['telephone_set-MAX_NUM_FORMS'] = ''

    def test_patient_create(self):
        """
        Testa inclusao de participante com campos obrigatorios
        """
        name = self._testMethodName
        self.data['name'] = name

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def test_anonymous_patient_create(self):
        """
        Testa inclusao de participante com campos obrigatórios quando este paciente é anônimo
        """

        data = {'anonymous': True,
                'date_birth': '01/02/1995',
                'gender': self.data["gender"],
                'telephone_set-TOTAL_FORMS': '3',
                'telephone_set-INITIAL_FORMS':'0',
                'telephone_set-MAX_NUM_FORMS': ''}

        self.client.post(reverse(PATIENT_NEW), data, follow=True)
        self.assertEqual(Patient.objects.filter(
            date_birth='1995-02-01',
            gender=self.data["gender"],
            name=None,
            cpf=None).count(), 1)

    def fill_social_demographic_data(self):
        """ Criar uma opcao de Schooling """
        school = Schooling.objects.create(name='Fundamental Completo')
        school.pk = '2'
        school.save()

        self.data['citizenship'] = ''
        self.data['natural_of'] = ''
        self.data['house_maid'] = '0'
        self.data['religion'] = '',
        self.data['amount_cigarettes'] = ''
        self.data['dvd'] = '1'
        self.data['wash_machine'] = '1'
        self.data['refrigerator'] = '1'
        self.data['schooling'] = school.pk
        self.data['freezer'] = '0'
        self.data['tv'] = '1'
        self.data['bath'] = '1'
        self.data['radio'] = '1'
        self.data['automobile'] = '1'

    def test_patient_social_demographic_data(self):
        """
        Test the inclusion of a patient with required fields and update of
        social demographic data.
        """

        # This data is required for the ManagementForm. This form is used
        # by the formset to manage the collection of forms contained in the
        # formset.
        self.fill_management_form()

        response = self.client.post(
            reverse(PATIENT_NEW), self.data, follow=True
        )
        self.assertEqual(
            Patient.objects.filter(name=self.data['name']).count(), 1
        )
        self.assertNotContains(response, _('Social class was not calculated'))

        # Prepare to test social demographic data tab
        patient_to_update = \
            Patient.objects.filter(name=self.data['name']).first()
        self.fill_social_demographic_data()
        self.data['currentTab'] = 1

        # Success case
        response = self.client.post(reverse(
            PATIENT_EDIT, args=(patient_to_update.pk,)), self.data,
            follow=True
        )
        self.assertEqual(
            Patient.objects.filter(name=self.data['name']).count(), 1
        )
        self.assertContains(
            response, _('Social demographic data successfully written.')
        )
        self.assertNotContains(response, _('Social class was not calculated'))

        # Error case
        self.data.pop('wash_machine')
        response = self.client.post(reverse(
            PATIENT_EDIT, args=(patient_to_update.pk,)), self.data,
            follow=True
        )
        self.assertContains(response, _('Social class was not calculated'))

    def fill_social_history_data(self):
        amount_cigarettes = AmountCigarettes.objects.create(name=_('Less than 1 pack'))
        amount_cigarettes.save()

        alcohol_frequency = AlcoholFrequency.objects.create(name=_('Sporadically'))
        alcohol_frequency.save()

        alcohol_period = AlcoholPeriod.objects.create(name=_('Less than 1 year'))
        alcohol_period.save()

        self.data['smoker'] = True
        self.data['amount_cigarettes'] = amount_cigarettes.pk
        self.data['ex_smoker'] = False
        self.data['alcoholic'] = True,
        self.data['alcohol_frequency'] = alcohol_frequency.pk
        self.data['alcohol_period'] = alcohol_period.pk
        self.data['drugs'] = 'ja_fez'

    def test_smoker_patient_can_not_be_ex_smoker(self):
        name = 'smoker_patient_ES'
        self.data['name'] = name

        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        # Prepare to test social history data tab
        patient_to_update = Patient.objects.filter(name=name).first()
        self.data['smoker'] = True
        self.data['ex_smoker'] = True
        self.data['currentTab'] = 2

        response = self.client.post(reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, _('Social history successfully recorded.'))

    def test_non_smoker_patient_can_not_fill_amount_of_cigarettes(self):
        name = 'non_smoker_AC'
        self.data['name'] = name

        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        # Prepare to test social history data tab
        patient_to_update = Patient.objects.filter(name=name).first()

        amount_cigarettes = AmountCigarettes.objects.create(name=_('Less than 1 pack'))
        amount_cigarettes.save()

        self.data['smoker'] = False
        self.data['amount_cigarettes'] = amount_cigarettes.pk
        self.data['currentTab'] = 2

        response = self.client.post(reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, _('Social history successfully recorded.'))

    def test_non_alcoholic_patient_can_not_fill_alcohol_frequency(self):
        name = 'non_alcoholic_AF'
        self.data['name'] = name

        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        # Prepare to test social history data tab
        patient_to_update = Patient.objects.filter(name=name).first()

        alcohol_frequency = AlcoholFrequency.objects.create(name=_('Sporadically'))
        alcohol_frequency.save()

        self.data['alcoholic'] = False
        self.data['alcohol_frequency'] = alcohol_frequency.pk
        self.data['currentTab'] = 2

        response = self.client.post(reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, _('Social history successfully recorded.'))

    def test_non_alcoholic_patient_can_not_fill_alcohol_period(self):
        name = 'non_alcoholic_AP'
        self.data['name'] = name

        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        # Prepare to test social history data tab
        patient_to_update = Patient.objects.filter(name=name).first()

        alcohol_period= AlcoholPeriod.objects.create(name=_('Less than 1 year'))
        alcohol_period.save()

        self.data['smoker'] = False
        self.data['alcohol_period'] = alcohol_period.pk
        self.data['currentTab'] = 2

        response = self.client.post(reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, _('Social history successfully recorded.'))

    def test_patient_social_history_data(self):
        """
        Test the inclusion of a patient with required fields and update of social history data
        """
        name = self._testMethodName
        self.data['name'] = name

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        # Prepare to test social history data tab
        patient_to_update = Patient.objects.filter(name=name).first()
        self.fill_social_history_data()
        self.data['currentTab'] = 2

        # Success case
        response = self.client.post(
            reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertContains(response, _('Social history successfully recorded.'))

    def test_patient_valid_email(self):
        """
        Teste de email invalido
        """

        self.data['email'] = 'mail@invalid.'

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, _('Incorrect e-mail'))

    def test_patient_valid_name(self):
        """
        Teste de validacao do campo nome completo  - obrigatorio
        """

        self.data['name'] = ''

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, _('Name must be included'))

    def test_patient_view_and_search(self):
        """
        Teste de visualizacao de participante apos cadastro na base de dados
        """

        patient_mock = self.util.create_patient(changed_by=self.user)
        patient_mock.cpf = '374.276.738-08'  # to test search for cpf
        patient_mock.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse('patient_view', args=[patient_mock.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = patient_view(request, patient_id=patient_mock.pk)
        self.assertEqual(response.status_code, 200)

        self.data[SEARCH_TEXT] = 'Patient'
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient_mock.name)
        self.assertEqual(response.context['patients'].count(), 1)

        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'].count(), 1)
        self.assertContains(response, patient_mock.cpf)

        self.data[SEARCH_TEXT] = ''
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'], '')

    def test_patient_list(self):
        """
        Teste a visualizacao de participante
        """
        patient_mock = self.util.create_patient(changed_by=self.user)

        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]))
        request.user = self.user

        response = patient_view(request, patient_mock.pk)
        self.assertEqual(response.status_code, 200)

    def test_patient_update_and_remove(self):
        """Teste de participante existente na base de dados """

        nameMethod = self._testMethodName
        userMethod = self.user
        patient_mock = self.util.create_patient(nameMethod, userMethod)
        # To test posting cpf patient attribute (patient_mock.cpf value
        # is due to what it was before creating this attribute value with
        # faker).
        patient_mock.cpf = '374.276.738-08'
        patient_mock.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]))
        request.user = self.user

        # This data is required for the ManagementForm. This form is used
        # by the formset to manage the collection of forms contained in the
        # formset.
        self.fill_management_form()

        response = patient_update(request, patient_id=patient_mock.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data['currentTab'] = 0
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data[CPF_ID] = ''
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data[CPF_ID] = patient_mock.cpf
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        # Inicio do CPF inserido no self.data para retorno positivo na busca
        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient_mock.cpf)

        self.data[ACTION] = 'remove'
        response = self.client.post(reverse(PATIENT_VIEW, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data[ACTION] = 'not'
        response = self.client.post(reverse(PATIENT_VIEW, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        patient_removed = Patient.objects.get(pk=patient_mock.pk)
        self.assertEqual(patient_removed.removed, True)

        # Inicio do CPF inserido no self.data - nao eh pra haver retorno para este inicio de CPF
        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, patient_mock.cpf)

    def test_remove_patient_get(self):
        patient_mock = self.util.create_patient(changed_by=self.user)

        count_patients = Patient.objects.count()

        self.assertEqual(count_patients, 1)

        self.data[ACTION] = 'remove'
        request = self.factory.get(reverse(PATIENT_EDIT, args=[patient_mock.pk]))
        request.user = self.user

        patient_update(request=request, patient_id=patient_mock.pk)
        patient_mock = get_object_or_404(Patient, id=patient_mock.pk)

        self.assertEqual(patient_mock.removed, False)

    def test_update_patient_not_exist(self):
        """Teste de participante nao existente na base de dados """

        # ID de participante nao existente na base
        id_patient = 99999

        # Create an instance of a GET request.
        request = self.factory.get(reverse(PATIENT_VIEW, args=[id_patient, ]))
        request.user = self.user

        try:
            response = patient_update(request, patient_id=id_patient)
            self.assertEqual(response.status_code, 404)
        except Http404:
            pass

    def test_patient_restore(self):
        """
        Tests removed patient recovering
        """
        # Creates participant already removed
        patient_mock = self.util.create_patient(changed_by=self.user)
        patient_mock.cpf = '374.276.738-08'  # to test search for cpf
        patient_mock.removed = True
        patient_mock.save()

        # Create an instance of a GET request.
        request = self.factory.get(
            reverse(PATIENT_VIEW, args=[patient_mock.pk, ])
        )
        request.user = self.user

        self.data['search_text'] = 374
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, patient_mock.cpf)

        response = restore_patient(request, patient_id=patient_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Patient.objects.filter(name=patient_mock.name).exclude(removed=True).count(), 1)

        self.data['search_text'] = 374
        response = self.client.post(reverse(PATIENT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient_mock.cpf)

    def test_views(self):
        """
        Tests aleatorios de views para checar robustez
        """
        client = Client()
        self.assertEqual(client.get('/response').status_code, 404)
        self.assertEqual(client.get('/notfound').status_code, 404)
        self.assertEqual(client.get('/patient/999999/').status_code, 302)
        self.assertEqual(client.get('/error').status_code, 404)
        self.assertEqual(client.get('/redirect_response').status_code, 404)
        self.assertEqual(client.get('/redirect_notfound').status_code, 404)
        self.assertEqual(client.get('/redirect_redirect_response').status_code, 404)
        self.assertEqual(client.get('/patient/find').status_code, 301)

    def test_patient_verify_homonym(self):
        """  Testar a busca por homonimo """
        patient_mock = self.util.create_patient(changed_by=self.user)

        # Busca valida
        self.data[SEARCH_TEXT] = patient_mock.name
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

        response = self.client.post(reverse('patients_verify_homonym_excluded'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)

        self.data[SEARCH_TEXT] = patient_mock.cpf
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

        response = self.client.post(reverse('patients_verify_homonym_excluded'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)

        # A search for an empty name returns no list, instead of an empty list.
        self.data[SEARCH_TEXT] = ''
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'], '')

        # Busca invalida
        self.data[SEARCH_TEXT] = '!@#'
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        patient_mock.removed = True
        patient_mock.save()

        self.data[SEARCH_TEXT] = patient_mock.name

        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        response = self.client.post(reverse('patients_verify_homonym_excluded'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)

        self.data[SEARCH_TEXT] = patient_mock.cpf

        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        response = self.client.post(reverse('patients_verify_homonym_excluded'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)


class MedicalRecordFormValidation(TestCase):
    user = ''
    data = {}
    util = UtilTests()

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """

        # print('Set up for', self._testMethodName)

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def fill_exam_record(self, test_file=True):
        self.data['description'] = 'Hemograma'
        self.data['doctor'] = 'Dr Medico'
        self.data['exam_site'] = 'Hospital'
        self.data['doctor_register'] = '1111'
        self.data['action'] = 'save'
        self.data['date'] = '10/05/2005'

        if test_file:
            file_to_test = SimpleUploadedFile('patient/exam_file.txt', b'rb')
            self.data['content'] = file_to_test

    def test_diagnosis_create_and_delete(self):
        """
        Testar a criação, leitura, atualização e exclusão do Diagnóstico
        """

        # Create mock objects to tests
        self.util.create_cid10_to_search()
        cid10_mock = ClassificationOfDiseases.objects.filter(code='B01').first()
        patient_mock = self.util.create_patient(changed_by=self.user)
        medical_record_mock = self.util.create_medical_record(self.user, patient_mock)

        request = self.factory.get(
            reverse('diagnosis_create', args=[patient_mock.pk, medical_record_mock.pk, cid10_mock.id, ]))
        request.user = self.user
        response = diagnosis_create(request, patient_id=patient_mock.pk, medical_record_id=medical_record_mock.pk,
                                    cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        diagnosis_mock = self.util.create_diagnosis(medical_record_mock)

        # Test for diagnosis delete
        count_diagnosis = Diagnosis.objects.all().count()

        response = self.client.post(
            reverse('diagnosis_delete', args=(patient_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.all().count(), count_diagnosis - 1)

    def test_medical_record_crud(self):
        """
        Testar a criação, leitura, atualização e exclusão do Avaliação Medica (MedicalRecord)
        """
        patient_mock = self.util.create_patient(changed_by=self.user)
        cid10_mock = self.util.create_cid10()

        # Create a new Medical Record and check if it created with successfully
        url = reverse('medical_record_new', args=(patient_mock.pk,))
        response = self.client.post(url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # It test uses a GET method. Create an instance of a GET request -
        request = self.factory.get(reverse('medical_record_diagnosis_create', args=[patient_mock.pk, cid10_mock.pk, ]))
        request.user = self.user
        response = medical_record_create_diagnosis_create(request, patient_id=patient_mock.pk, cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        # Test a Medical Record View method
        medical_record_data = MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()

        url = reverse('medical_record_view', args=[patient_mock.pk, medical_record_data.pk, ])

        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_view(request, patient_mock.pk, medical_record_data.pk)
        self.assertEqual(response.status_code, 200)

        # It makes tests with a invalid ID for method medical record view
        try:
            url = reverse('medical_record_view', args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            self.assertRaises(medical_record_view(request, patient_mock.pk, 9999))

        except Http404:
            pass

    def test_medical_record_view(self):

        patient_mock = self.util.create_patient(changed_by=self.user)
        self.util.create_cid10()
        self.util.create_medical_record(self.user, patient_mock)

        response = self.client.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=3")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(medical_record_mock.pk, response.context['medical_record'])

    def test_medical_record_update(self):

        patient_mock = self.util.create_patient(changed_by=self.user)
        self.util.create_medical_record(self.user, patient_mock)

        response = self.client.get(reverse(PATIENT_EDIT, args=[patient_mock.pk]) + "?currentTab=3")
        self.assertEqual(response.status_code, 200)

        self.data['action'] = 'save'
        self.data['currentTab'] = 3
        self.data['nextTab'] = ""
        self.data['nextTabURL'] = ""
        url = reverse(PATIENT_EDIT, args=[patient_mock.pk])
        response = self.client.post(url + "?currentTab=3", self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # self.assertEqual(medical_record_mock.pk, response.context['medical_record'])

    def test_medical_record_edit(self):
        """
        Testar a edição de avaliação medica
        """

        patient_mock = self.util.create_patient(changed_by=self.user)
        medical_record_mock = self.util.create_medical_record(self.user, patient_mock)
        # Test a medical record edit method - no changes it will occurs - just pass by the method
        url = reverse("medical_record_edit", args=[patient_mock.pk, medical_record_mock.pk, ])
        request = self.factory.get(url + "?status=edit")
        request.user = self.user

        response = medical_record_update(request, patient_id=patient_mock.pk, record_id=medical_record_mock.pk)
        self.assertEqual(response.status_code, 200)

        # It makes tests with a invalid ID for method medical record edit
        try:
            url = reverse("medical_record_edit", args=[patient_mock.pk, 9999, ])
            request = self.factory.get(url + "?status=edit")
            request.user = self.user
            response = medical_record_update(request, patient_id=patient_mock.pk, record_id=9999)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

        # It will coverage all method - medical record edit
        self.data['action'] = ''
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 200)

        self.data['action'] = 'finish'
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk,))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 302)

        # diagnosis update
        diagnosis_mock = self.util.create_diagnosis(medical_record_mock)
        diagnosis_id = diagnosis_mock.pk  # classification_of_diseases_id

        count_diagnosis = Diagnosis.objects.all().count()
        self.data['action'] = 'detail-' + str(diagnosis_id)
        self.data['description-' + str(diagnosis_id)] = diagnosis_mock.classification_of_diseases.description
        self.data['date-' + str(diagnosis_id)] = '21/02/2015'
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk))
        response = self.client.post(url + "?status=edit", self.data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.all().count(), count_diagnosis)
        self.assertEqual(Diagnosis.objects.filter(pk=diagnosis_id, date='2015-02-21').count(), 1)

        # incorrect date
        self.data['date-' + str(diagnosis_id)] = '99/02/2015'
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Diagnosis.objects.filter(pk=diagnosis_id, date='2015-02-21').count(), 1)

        # no date
        self.data['date-' + str(diagnosis_id)] = ''
        url = reverse('medical_record_edit', args=(patient_mock.pk, medical_record_mock.pk))
        response = self.client.post(url + "?status=edit", self.data)
        self.assertEqual(response.status_code, 302)

    def test_exam_create(self):
        """
        Testar a criação de exames
        """
        patient_mock = self.util.create_patient(changed_by=self.user)
        medical_record_mock = self.util.create_medical_record(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis(medical_record_mock)

        count_exams = ComplementaryExam.objects.all().count()

        # A simple test of Exam Create Method.
        request = self.factory.get(
            reverse('exam_create', args=[patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk, ]))
        request.user = self.user

        response = exam_create(request, patient_id=patient_mock.pk, record_id=medical_record_mock.pk,
                               diagnosis_id=diagnosis_mock.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

        # Test of Exam Create with file attachment
        self.fill_exam_record()

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 1)

        # Test of exam Create withoud file attachment
        self.fill_exam_record(test_file=False)
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 2)

        # A tests more conditionals of exam create method.
        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 3)

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertGreaterEqual(ComplementaryExam.objects.all().count(), 1)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 4)

    def create_complementary_exam(self, patient_mock, medical_record_mock, diagnosis_mock):
        """
        Testar a inclusao de exames complementares
        """
        self.fill_exam_record()

        count_exams = ComplementaryExam.objects.all().count()

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 1)

    def test_exam_update(self):
        """
        Testar a atualização de um exame complementar
        """
        patient_mock = self.util.create_patient(changed_by=self.user)
        medical_record_mock = self.util.create_medical_record(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis(medical_record_mock)

        self.create_complementary_exam(patient_mock, medical_record_mock, diagnosis_mock)
        count_exams = ComplementaryExam.objects.all().count()

        # Tests for exam edit method
        complementary_exam = ComplementaryExam.objects.all().first()

        self.fill_exam_record()
        self.data['action'] = 'save'
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

        # Tests delete file from exam
        exams_file = ExamFile.objects.all()
        for exam_file in exams_file:
            response = self.client.post(
                reverse('exam_file_delete', args=(exam_file.id,)), self.data)
            self.assertEqual(response.status_code, 302)

    def test_exam_file_upload(self):
        """
        Testar a adição de exame com arquivo anexo - inclusao e remoção
        """
        try:
            patient_mock = self.util.create_patient(changed_by=self.user)
            medical_record_mock = self.util.create_medical_record(self.user, patient_mock)
            diagnosis_mock = self.util.create_diagnosis(medical_record_mock)

            # Tests for exam edit method
            self.create_complementary_exam(patient_mock, medical_record_mock, diagnosis_mock)
            complementary_exam = ComplementaryExam.objects.all().first()
            # count_exams = ComplementaryExam.objects.all().count()

            self.data['status'] = 'edit'
            request = self.factory.get(
                reverse('exam_view', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
            request.user = self.user
            response = exam_view(request, patient_mock.pk, medical_record_mock.pk, complementary_exam.pk)
            self.assertEqual(response.status_code, 200)

            # Tests delete file from exam
            exam_file = ExamFile.objects.all().first()

            response = self.client.post(
                reverse('exam_file_delete', args=(exam_file.id,)), self.data)
            self.assertEqual(response.status_code, 302)

            # It will delete first exam created
            response = self.client.post(
                reverse('exam_delete', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)),
                self.data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(ComplementaryExam.objects.all().count(), 0)
        finally:
            exams_file = ExamFile.objects.all()
            for exam_file in exams_file:
                exam_file.content.delete()

    def test_cid_search(self):
        """
        Testa busca pelo CID
        """

        search_text_meta = 'search_text'
        group_id_meta = 'group_id'

        # Create a cids to make search.
        self.util.create_cid10_to_search()

        # Busca valida
        self.data['medical_record'] = ''
        self.data['patient_id'] = ''
        self.data[search_text_meta] = 'A'
        self.data[group_id_meta] = 1
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paratifoide')

        self.data[search_text_meta] = 'B'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tifoide')

        self.data[search_text_meta] = '01'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Febres')
        self.assertEqual(response.context['cid_10_list'].count(), 2)

        # Busca invalida
        self.data[search_text_meta] = 'ZZZA1'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'].count(), 0)

        self.data[search_text_meta] = ''
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'], '')


class QuestionnaireFormValidation(TestCase):
    """
    For this test to be executed, it is necessary to
    have the following survey on LimeSurvey:

    - questionnaire with no answers (CLEAN_QUESTIONNAIRE)
    - questionnaire incomplete (INCOMPLETE_QUESTIONNAIRE)
    - questionnaire completed filled (FILLED_QUESTIONNAIRE)
    - questionnaire with error: tokens table not started (NO_TOKEN_TABLE)
    - questionnaire with error: questionnaire not activated (QUESTIONNAIRE_NOT_ACTIVE)
    - questionnaire with error: missing standard fields (MISSING_STANDARD_FIEDS)
    - questionnaire with error: token not generated (TOKEN_NOT_GENERATED)
    - questionnaire with error: invalid survey (SURVEY_INVALID)
    """

    user = ''
    data = {}
    util = UtilTests()

    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def test_entrance_evaluation_response_view(self):
        """
        Test list of entrance evaluation
        of the entrance evaluation questionnaire type
        """
        name_method = self._testMethodName
        user_method = self.user
        patient_mock = self.util.create_patient(name_method, user_method)

        response = self.client.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_questionnaires_data_list'], [])

        # LimeSurvey system not available
        settings.LIMESURVEY['URL_API'] = 'https://surveys.numec.prp.usp.br/'  # with error
        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=4")
        request.user = user_method
        request.LANGUAGE_CODE = 'pt-BR'

        # this was done in order to error messages can be "presented"
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = patient_view(request, patient_mock.pk)
        self.assertEqual(response.status_code, 200)

        # return to correct url
        settings.LIMESURVEY['URL_API'] = 'https://survey.numec.prp.usp.br/'

        # new filling - creating one survey - no responses
        survey_mock = self.util.create_survey_mock(CLEAN_QUESTIONNAIRE, True)

        response = self.client.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['patient_questionnaires_data_list']), 1)
        self.assertEqual(response.context['patient_questionnaires_data_list'][0]['survey_id'], survey_mock.pk)
        self.assertEqual(response.context['patient_questionnaires_data_list'][0]['limesurvey_id'],
                         survey_mock.lime_survey_id)
        self.assertEqual(len(response.context['patient_questionnaires_data_list'][0]['questionnaire_responses']), 0)

        # including a new survey response...
        response_survey_mock = self.util.create_response_survey_mock(user_method, patient_mock, survey_mock)
        response = self.client.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=4")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['patient_questionnaires_data_list']), 1)
        entrance_evaluation = response.context['patient_questionnaires_data_list'][0]
        self.assertEqual(len(entrance_evaluation['questionnaire_responses']), 1)
        response_survey = entrance_evaluation['questionnaire_responses'][0]['questionnaire_response']
        self.assertEqual(response_survey.token_id, int(response_survey_mock.token_id))

        completed = entrance_evaluation['questionnaire_responses'][0]['completed']
        self.assertTrue(not completed)  # questionnaire is not completed

    def test_check_limesurvey_availability(self):
        """
        Test to see if LimeSurvey is available under circumstances
        """
        namemethod = self._testMethodName
        usermethod = self.user
        patient_mock = self.util.create_patient(namemethod, usermethod)

        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]) + "?currentTab=4")
        request.user = self.user

        # test limesurvey available
        surveys = Questionnaires()

        self.assertTrue(check_limesurvey_access(request, surveys))

        surveys.release_session_key()

        # test limesurvey not available
        settings.LIMESURVEY['URL_API'] = 'https://surveys.numec.prp.usp.br/'  # with error

        surveys = Questionnaires()

        with self.assertRaises(MessageFailure):
            check_limesurvey_access(request, surveys)

        surveys.release_session_key()

        settings.LIMESURVEY['URL_API'] = 'https://survey.numec.prp.usp.br/'  # without error

    def test_entrance_evaluation_response_create(self):
        # """
        # Test inclusion of questionnaire response to a clear survey
        # of the type: entrance evaluation questionnaire
        # """
        # create mock patient, questionnaire

        name_method = self._testMethodName
        user_method = self.user
        patient_mock = self.util.create_patient(name_method, user_method)

        survey_mock = self.util.create_survey_mock(CLEAN_QUESTIONNAIRE, True)

        self.data['date'] = '01/09/2014'
        self.data['action'] = 'save'
        self.data['initial-date'] = '2015-09-02'

        url = reverse(QUESTIONNAIRE_NEW, args=(patient_mock.pk, survey_mock.pk,))
        response = self.client.post(url + "?origin=subject", self.data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_entrance_evaluation_response_update(self):
        """
        Test update of questionnaire response to a clear survey
        of the type: entrance evaluation questionnaire
        """
        name_method = self._testMethodName
        user_method = self.user
        patient_mock = self.util.create_patient(name_method, user_method)

        survey_mock = self.util.create_survey_mock(CLEAN_QUESTIONNAIRE, True)

        response_survey_mock = self.util.create_response_survey_mock(
            user_method, patient_mock, survey_mock, 12
        )

        url1 = reverse(QUESTIONNAIRE_EDIT, args=[response_survey_mock.pk], current_app='patient')
        url2 = url1.replace('experiment', 'patient')

        response = self.client.get(url2 + "?origin=subject&status=edit")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_survey_mock.token_id, response.context["questionnaire_response"].token_id)

        self.data['action'] = 'save'
        response = self.client.post(url2 + "?origin=subject&status=edit", self.data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_entrance_evaluation_response_delete(self):
        """
        Test delete from 2 views: update and view
        of the type: entrance evaluation questionnaire
        """
        namemethod = self._testMethodName
        usermethod = self.user
        patient_mock = self.util.create_patient(namemethod, usermethod)

        survey_mock = self.util.create_survey_mock(CLEAN_QUESTIONNAIRE, True)

        # response_survey_mock = self.util.create_response_survey_mock(self.user, patient_mock, survey_mock)
        response_survey_mock = self.util.create_response_survey_mock(usermethod, patient_mock, survey_mock)

        # delete questionnaire response when it is in mode
        url1 = reverse(QUESTIONNAIRE_VIEW, args=[response_survey_mock.pk], current_app='patient')
        url2 = url1.replace('experiment', 'patient')
        self.data['action'] = 'remove'
        response = self.client.post(url2 + "?origin=subject&status=edit", self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # workaround because reverse is getting experiment url instead of patient
        url1 = reverse(QUESTIONNAIRE_EDIT, args=[response_survey_mock.pk], current_app='patient')
        url2 = url1.replace('experiment', 'patient')

        self.data['action'] = 'remove'
        response = self.client.post(url2 + "?origin=subject&status=edit", self.data, follow=True)
        self.assertEqual(response.status_code, 404)  # error - response already deleted

        response_survey_mock = self.util.create_response_survey_mock(usermethod, patient_mock, survey_mock)

        # workaround because reverse is getting experiment url instead of patient
        url1 = reverse(QUESTIONNAIRE_EDIT, args=[response_survey_mock.pk], current_app='patient')
        url2 = url1.replace('experiment', 'patient')

        self.data['action'] = 'remove'
        response = self.client.post(url2 + "?origin=subject&status=edit", self.data, follow=True)
        self.assertEqual(response.status_code, 200)  # now it is deleted

    def test_entrance_ev_response_complete(self):
        """
        Test view of questionnaire response when questionnaire is complete
        of the type: entrance evaluation questionnaire
        """
        namemethod = self._testMethodName
        usermethod = self.user
        patient_mock = self.util.create_patient(namemethod, usermethod)
        survey_mock = self.util.create_survey_mock(CLEAN_QUESTIONNAIRE, True)
        response_survey_mock = self.util.create_response_survey_mock(self.user, patient_mock, survey_mock, 2)

        url1 = reverse(QUESTIONNAIRE_VIEW, args=[response_survey_mock.pk], current_app='patient')
        url2 = url1.replace('experiment', 'patient')
        response = self.client.get(url2 + "?origin=subject&status=edit")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_survey_mock.token_id, response.context["questionnaire_response"].token_id)

    def _test_experiment_response_view(self):
        """
        Testa a visualizacao completa do questionario respondido no Lime Survey
        """

        # Create a research project
        research_project = ResearchProject.objects.create(title="Research project title",
                                                          start_date=date.today(),
                                                          description="Research project description")
        research_project.save()

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update",
                                               research_project=research_project)
        experiment.save()

        # Create the root of the experimental protocol
        block = Block.objects.create(identification='Root',
                                     description='Root description',
                                     experiment=Experiment.objects.first(),
                                     component_type='block',
                                     type="sequence")
        block.save()

        # Create a quesitonnaire at LiveSurvey to use in this test.
        survey_title = 'Questionario de teste - DjangoTests'

        lime_survey = Questionnaires()
        sid = lime_survey.add_survey(99999, survey_title, 'en', 'G')
        lime_survey.release_session_key()

        try:
            new_survey, created = Survey.objects.get_or_create(lime_survey_id=sid,
                                                               is_initial_evaluation=False)  # Create a questionnaire
            questionnaire = Questionnaire.objects.create(identification='Questionnaire',
                                                         description='Questionnaire description',
                                                         experiment=Experiment.objects.first(),
                                                         component_type='questionnaire',
                                                         survey=new_survey)
            questionnaire.save()

            # Include the questionnaire in the root.
            component_configuration = ComponentConfiguration.objects.create(
                name='ComponentConfiguration',
                parent=block,
                component=questionnaire
            )
            component_configuration.save()

            data_configuration_tree = DataConfigurationTree.objects.create(
                component_configuration=component_configuration
            )
            data_configuration_tree.save()

            # Criar um grupo mock para ser utilizado no teste
            group = Group.objects.create(experiment=experiment,
                                         title="Group-update",
                                         description="Descricao do Group-update",
                                         experimental_protocol_id=block.id)
            group.save()

            # Criar um Subject para o experimento
            patient_mock = self.util.create_patient(changed_by=self.user)

            subject_mock = Subject(patient=patient_mock)
            subject_mock.save()

            subject_group = SubjectOfGroup(subject=subject_mock, group=group)
            subject_group.save()

            group.subjectofgroup_set.add(subject_group)
            # experiment.save()

            # Pretend we have a response
            questionnaire_response = ExperimentQuestionnaireResponse()
            questionnaire_response.data_configuration_tree = data_configuration_tree
            questionnaire_response.subject_of_group = subject_group
            questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
            questionnaire_response.questionnaire_responsible = self.user
            questionnaire_response.date = datetime.now()
            questionnaire_response.save()

            # Visualiza preenchimento da Survey
            self.data['currentTab'] = 4

            url = reverse(PATIENT_VIEW, args=[patient_mock.pk, ])

            response = self.client.get(url + "?currentTab=4", data=self.data)
            # We don't get any error, because the method get_questionnaire_responses called by
            # questionnaire_response_edit simply returns an empty list of responses.
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['patient_questionnaires_data_list']), 0)  # no entrance evaluation
            self.assertEqual(len(response.context['questionnaires_data']), 1)  # experiment questionnaire

        finally:
            # Deleta a survey gerada no Lime Survey
            lime_survey = Questionnaires()
            status = lime_survey.delete_survey(sid)
            lime_survey.release_session_key()
            self.assertEqual(status, 'OK')


class TranslationValidation(TestCase):
    """
    For this test to be executed, it is necessary to
    have the following files to be translated:

    - load_initial_data.json (fixtures directory) - to initialize data in database
    """

    user = ''
    data = {}
    util = UtilTests()

    xml_data = '''<ClaML version="2.0.0">
    <Meta name="TopLevelSort" value="I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII"/>
    <Meta name="lang" value="en"/>
    <Identifier authority="WHO" uid="icd10_2016"/>
    <Title date="2014-10-14" name="ICD-10-EN-2016" version="2016">International Statistical Classification of Diseases
        and Related Health Problems 10th Revision
    </Title>
    <ClassKinds>
        <ClassKind name="category"/>
        <ClassKind name="block"/>
        <ClassKind name="chapter"/>
    </ClassKinds>
    <UsageKinds>
        <UsageKind mark="*" name="aster"/>
        <UsageKind mark="+" name="dagger"/>
    </UsageKinds>

    <Class code="A01" kind="category">
        <Meta name="MortBCode" value="058"/>
        <Meta name="MortL4Code" value="4-016"/>
        <Meta name="MortL3Code" value="3-018"/>
        <Meta name="MortL2Code" value="2-025"/>
        <Meta name="MortL1Code" value="1-027"/>
        <SuperClass code="C00-C14"/>
        <SubClass code="C05.0"/>
        <SubClass code="C05.1"/>
        <SubClass code="C05.2"/>
        <SubClass code="C05.8"/>
        <SubClass code="C05.9"/>
        <Rubric id="D0001818" kind="preferred">
            <Label xml:lang="en" xml:space="default">Malignant neoplasm of palate</Label>
        </Rubric>
    </Class>
    <Class code="C05.0" kind="category">
        <Meta name="MortBCode" value="058"/>
        <Meta name="MortL4Code" value="4-016"/>
        <Meta name="MortL3Code" value="3-018"/>
        <Meta name="MortL2Code" value="2-025"/>
        <Meta name="MortL1Code" value="1-027"/>
        <SuperClass code="C05"/>
        <Rubric id="id-to-be-added-later-1210506823253-239" kind="preferredLong">
            <Label xml:lang="en" xml:space="default">Malignant neoplasm: Hard palate</Label>
        </Rubric>
        <Rubric id="D0001819" kind="preferred">
            <Label xml:lang="en" xml:space="default">Hard palate</Label>
        </Rubric>
    </Class>

    <Class code="U85" kind="category">
        <Meta name="MortL1Code" value="UNDEF"/>
        <Meta name="MortL2Code" value="UNDEF"/>
        <Meta name="MortL3Code" value="UNDEF"/>
        <Meta name="MortL4Code" value="UNDEF"/>
        <Meta name="MortBCode" value="UNDEF"/>
        <SuperClass code="U82-U85"/>
        <Rubric id="id-WHOICD102010_v2011-January-11-1389184608984-20" kind="preferred">
          <Label xml:lang="en" xml:space="default">Vitamin B<Term class="subscript">12</Term> deficiency anaemia</Label>
        </Rubric>
        <Rubric id="id-WHOICD102010_v2011-January-11-1389184782897-0" kind="inclusion">
            <Label xml:lang="en" xml:space="default">Non-responsiveness to antineoplastic drugs</Label>
        </Rubric>
        <Rubric id="id-WHOICD102010_v2011-January-11-1389184782897-1" kind="inclusion">
            <Label xml:lang="en" xml:space="default">Refractory cancer</Label>
        </Rubric>
    </Class>
</ClaML>
        '''

    csv_data ='''Código ICD-10-CM,Long_Descp ICD-10-CM (EN_2017),Descrição longa PT Uniformizada (250 carateres),Descrição longa PT Curta (90 carateres)
A00,Cholera,Cólera,Cólera
A000,Cholera due to Vibrio cholerae 01 biovar cholerae,Cólera devida a Vibrio cholerae 01 estirpe cholerae,Cólera C Vibrio cholerae 01 estirpe cholerae
'''

    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.stdout_bk, sys.stdout = sys.stdout, open('/dev/null', 'w+')

    def tearDown(self):
        self.client.logout()
        sys.stdout.close()
        sys.stdout = self.stdout_bk

    def fill_en_icd_file(self):
        tree = XML(self.xml_data)

        return tree

    def create_xml_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.xml_data)

    @staticmethod
    def create_file_with_incorrect_data(filename):
        with open(filename, 'w') as f:
            f.write("incorrect data")
            f.close()

    def create_csv_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.csv_data)

    def test_classification_of_diseases_translate_into_english(self):
        # """
        # Test to initialize icd with English translation
        #
        # """

        classification_of_disease = self.util.create_cid10()
        classification_of_disease.description_en = None
        classification_of_disease.save()

        classification_of_disease = ClassificationOfDiseases.objects.first()

        self.assertIsNone(classification_of_disease.description_en)

        filename = os.path.join(settings.MEDIA_ROOT, "output.xml")

        self.create_xml_file(filename)

        # num_records_updated = icd_english_translation(tree)
        num_records_updated = import_classification_of_diseases(filename)

        os.remove(filename)

        classification_of_disease = ClassificationOfDiseases.objects.all()
        self.assertIsNotNone(classification_of_disease.first().description_en)
        self.assertEqual(num_records_updated, classification_of_disease.count())

    def test_check_filename(self):
        # """
        # Test to see if file is open correctly
        # """

        self.assertRaises(FileNotFoundError, import_classification_of_diseases, "incorrect_file_name")
        self.assertRaises(IOError, import_classification_of_diseases, "incorrect_file_name")

        filename = os.path.join(settings.MEDIA_ROOT, "output.xml")

        with open(filename, 'w') as f:
            f.write("incorrect data")
        f.close()

        self.assertRaises(ElementTree.ParseError, import_classification_of_diseases, filename)

        os.remove(filename)

    def test_translate_data_from_fixtures(self):
        filename = os.path.join(
            settings.BASE_DIR,
            os.path.join("patient", os.path.join("data_migrations", "0006_translate_data_into_english.json"))
        )
        # Does not display "Installed fixtures message"
        stdout_bk, sys.stdout = sys.stdout, open('/dev/null', 'w+')

        call_command('loaddata', "load_initial_data")
        # Recover default sys.stdout
        sys.stdout.close()
        sys.stdout = stdout_bk

        first_alcohol_frequency = AlcoholFrequency.objects.first()
        self.assertIsNotNone(AlcoholFrequency.objects.first().name_en)

        first_alcohol_frequency.name_en = None
        first_alcohol_frequency.save()
        self.assertIsNone(AlcoholFrequency.objects.first().name_en)

        fixtures_formatted_data = translate_fixtures_into_english(filename)
        # print(fixtures_formatted_data)
        update_translated_data(fixtures_formatted_data)

        self.assertIsNotNone(AlcoholFrequency.objects.first().name_en)

    def test_translate_icd_into_english_with_command(self):
        # """
        # Test to initialize icd with English translation using command (similar to python manage.py import_icd)
        #
        # """

        classification_of_disease = self.util.create_cid10()
        classification_of_disease.description_en = None
        classification_of_disease.save()

        classification_of_disease = ClassificationOfDiseases.objects.first()

        self.assertIsNone(classification_of_disease.description_en)

        filename = os.path.join(settings.MEDIA_ROOT, "output.xml")

        self.create_xml_file(filename)

        call_command("import_icd", en=filename)

        os.remove(filename)

        classification_of_disease = ClassificationOfDiseases.objects.all()
        self.assertIsNotNone(classification_of_disease.first().description_en)

        self.create_file_with_incorrect_data(filename)
        self.assertRaises(CommandError, call_command, "import_icd", en=filename)
        os.remove(filename)

    def test_translate_icd_cid_with_command(self):
        temp_dir = tempfile.mkdtemp()

        file_path = os.path.join(temp_dir, 'output.csv')
        self.create_csv_file(file_path)
        call_command("import_icd_cid", file=file_path)

        classification_of_disease = ClassificationOfDiseases.objects.all()
        self.assertIsNotNone(classification_of_disease.first().description_en)

        os.remove(file_path)

        self.assertEqual(2, ClassificationOfDiseases.objects.count())
