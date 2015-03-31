# -*- coding: UTF-8 -*-
from datetime import date

from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.http import Http404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import RequestFactory

from patient.models import ClassificationOfDiseases, MedicalRecordData, Diagnosis, ComplementaryExam, ExamFile, \
    Gender, Schooling, Patient, AlcoholFrequency, AlcoholPeriod, AmountCigarettes
from patient.views import medical_record_view, medical_record_update, diagnosis_create, \
    medical_record_create_diagnosis_create, exam_create, exam_view, \
    patient_update, patient_view, restore_patient, reverse
from custom_user.models import User
from patient.validation import CPF

# Constantes para testes de User
USER_EDIT = 'user_edit'
USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
USER_NEW = 'user_new'

# Constantes para testes paciente
ACTION = 'action'
CPF_ID = 'cpf'
SEARCH_TEXT = 'search_text'

PATIENT_SEARCH = 'patient_search'
PATIENT_VIEW = 'patient_view'
PATIENT_NEW = 'patient_new'
PATIENT_EDIT = 'patient_edit'


class UtilTests():

    def create_patient_mock(self, name='Pacient Test', user=None):
        """ Cria um paciente para ser utilizado durante os testes """
        gender = Gender.objects.create(name='Masculino')
        gender.save()

        p_mock = Patient()
        p_mock.name = name
        p_mock.date_birth = '2001-01-15'
        p_mock.cpf = '374.276.738-08'
        p_mock.gender = gender
        p_mock.changed_by = user
        p_mock.save()
        return p_mock

    def create_cid10_to_search(self):
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()
        cid10 = ClassificationOfDiseases.objects.create(code='B01', description='Febres tifoide ',
                                                        abbreviated_description='B01 Febres tifoide ')
        cid10.save()

    def create_cid10_mock(self):
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()

        return cid10

    def create_medical_record_mock(self, user, new_patient):
        medical_record = MedicalRecordData()
        medical_record.patient = new_patient
        medical_record.record_responsible = user
        medical_record.save()
        return medical_record

    def create_diagnosis_mock(self, medical_record):
        cid10_mock = self.create_cid10_mock()
        diagnosis = Diagnosis(medical_record_data=medical_record, classification_of_diseases=cid10_mock)
        diagnosis.save()

        return diagnosis


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
                     'email': 'email@email.com'
                     }

    def test_patient_invalid_cpf(self):
        """
        Testa inclusao de paciente com cpf invalido
        """

        # CPF invalido
        cpf = '100.913.651-81'
        self.data['cpf'] = cpf

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf", u'CPF ' + cpf + u' n\xe3o \xe9 v\xe1lido')

    def test_patient_empty_cpf(self):
        """
        Testa inclusao de paciente com cpf invalido
        """

        # CPF vazio
        name = self._testMethodName
        self.data['name'] = name
        self.data[CPF_ID] = ''

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def test_patient_future_date_birth(self):
        """
        Testa inclusao de paciente com data de nascimento futura
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
        Testa inclusao de paciente com data de nascimento futura
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
        Testa inclusao de paciente com campos obrigatorios
        """
        name = self._testMethodName
        self.data['name'] = name

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        self.data['currentTab'] = 0
        self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)


    def fill_social_demographic_data(self):
        """ Criar uma opcao de Schooling """

        school = Schooling.objects.create(name='Fundamental Completo')
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
        Test the inclusion of a patient with required fields and update of social demographic data
        """
        name = self._testMethodName
        self.data['name'] = name

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, u'Classe Social não calculada')

        # Prepare to test social demographic data tab
        patient_to_update = Patient.objects.filter(name=name).first()
        self.fill_social_demographic_data()
        self.data['currentTab'] = 1

        # Success case
        response = self.client.post(
            reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertContains(response, u'Dados sociodemográficos gravados com sucesso.')
        self.assertNotContains(response, u'Classe Social não calculada')

        # Error case
        self.data.pop('wash_machine')
        # name = 'test_patient_social_demographic_data_1'
        # self.data['name'] = name
        # self.data[CPF_ID] = ''
        # response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        response = self.client.post(
            reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertContains(response, u'Classe Social não calculada')


    def fill_social_history_data(self):
        amount_cigarettes = AmountCigarettes.objects.create(name='Menos de 1 maço')
        amount_cigarettes.save()

        alcohol_frequency = AlcoholFrequency.objects.create(name='Esporadicamente')
        alcohol_frequency.save()

        alcohol_period = AlcoholPeriod.objects.create(name='Menos de 1 ano')
        alcohol_period.save()

        self.data['smoker'] = True
        self.data['amount_cigarettes'] = amount_cigarettes.pk
        self.data['ex_smoker'] = False
        self.data['alcoholic'] = True,
        self.data['alcohol_frequency'] = alcohol_frequency.pk
        self.data['alcohol_period'] = alcohol_period.pk
        self.data['drugs'] = 'ja_fez'


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
        self.assertContains(response, u'História social gravada com sucesso.')


    def test_patient_valid_email(self):
        """
        Teste de email invalido
        """

        self.data['email'] = 'mail@invalid.'

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, 'Informe um endereço de email válido')

    def test_patient_valid_name(self):
        """
        Teste de validacao do campo nome completo  - obrigatorio
        """

        self.data['name'] = ''

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
        self.fill_management_form()

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, 'Nome deve ser preenchido')

    def test_patient_view_and_search(self):
        """
        Teste de visualizacao de paciente apos cadastro na base de dados
        """

        patient_mock = self.util.create_patient_mock(user=self.user)

        # Create an instance of a GET request.
        request = self.factory.get(reverse('patient_view', args=[patient_mock.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = patient_view(request, patient_id=patient_mock.pk)
        self.assertEqual(response.status_code, 200)

        self.data[SEARCH_TEXT] = 'Pacient'
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
        Teste a visualizacao de paciente
        """
        patient_mock = self.util.create_patient_mock(user=self.user)

        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]))
        request.user = self.user

        response = patient_view(request, patient_mock.pk)
        self.assertEqual(response.status_code, 200)

    def test_patient_update_and_remove(self):
        """Teste de paciente existente na base de dados """

        patient_mock = self.util.create_patient_mock(name='Pacient Test Update', user=self.user)

        # Create an instance of a GET request.
        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]))
        request.user = self.user

        # "This data is required for the ManagementForm. This form is used by the formset to manage the collection of
        # forms contained in the formset."
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
        patient_mock = self.util.create_patient_mock(user=self.user)

        count_patients = Patient.objects.count()

        self.assertEqual(count_patients, 1)

        self.data[ACTION] = 'remove'
        request = self.factory.get(reverse(PATIENT_EDIT, args=[patient_mock.pk]))
        request.user = self.user

        patient_update(request=request, patient_id=patient_mock.pk)
        patient_mock = get_object_or_404(Patient, id=patient_mock.pk)

        self.assertEqual(patient_mock.removed, False)

    def test_update_patient_not_exist(self):
        """Teste de paciente nao existente na base de dados """

        # ID de paciente nao existente na base
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
        """Testa a recuperaracao de paciente removido """

        # Cria um paciente ja removido no BD
        patient_mock = self.util.create_patient_mock(user=self.user)
        patient_mock.removed = True
        patient_mock.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk, ]))
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
        patient_mock = self.util.create_patient_mock(user=self.user)

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
        # print 'Set up for', self._testMethodName

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
        self.data['action'] = 'upload'
        self.data['date'] = '10/05/2005'

        if test_file:
            file_to_test = SimpleUploadedFile('patient/exam_file.txt', 'rb')
            self.data['content'] = file_to_test

    def test_diagnosis_create_and_delete(self):
        """
        Testar a criação, leitura, atualização e exclusão do Diagnóstico
        """

        # Create mock objects to tests
        self.util.create_cid10_to_search()
        cid10_mock = ClassificationOfDiseases.objects.filter(code='B01').first()
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)

        request = self.factory.get(
            reverse('diagnosis_create', args=[patient_mock.pk, medical_record_mock.pk, cid10_mock.id, ]))
        request.user = self.user
        response = diagnosis_create(request, patient_id=patient_mock.pk, medical_record_id=medical_record_mock.pk,
                                    cid10_id=cid10_mock.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diagnosis.objects.filter(medical_record_data=MedicalRecordData.objects.filter(
            patient_id=Patient.objects.get(pk=patient_mock.pk)).first()).count(), 1)

        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

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
        patient_mock = self.util.create_patient_mock(user=self.user)
        cid10_mock = self.util.create_cid10_mock()

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

    def test_medical_record_edit(self):
        """
        Testar a edição de avaliação medica
        """

        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
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

    def test_exam_create(self):
        """
        Testar a criação de exames
        """
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

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

        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 4)

        response = self.client.post(
            reverse('exam_create', args=(patient_mock.pk, medical_record_mock.pk, diagnosis_mock.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertGreaterEqual(ComplementaryExam.objects.all().count(), 1)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams + 5)

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
        patient_mock = self.util.create_patient_mock(user=self.user)
        medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
        diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

        self.create_complementary_exam(patient_mock, medical_record_mock, diagnosis_mock)
        count_exams = ComplementaryExam.objects.all().count()

        # Tests for exam edit method
        complementary_exam = ComplementaryExam.objects.all().first()

        self.fill_exam_record(test_file=False)
        self.data['action'] = ''
        response = self.client.post(
            reverse('exam_edit', args=(patient_mock.pk, medical_record_mock.pk, complementary_exam.pk,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ComplementaryExam.objects.all().count(), count_exams)

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
            patient_mock = self.util.create_patient_mock(user=self.user)
            medical_record_mock = self.util.create_medical_record_mock(self.user, patient_mock)
            diagnosis_mock = self.util.create_diagnosis_mock(medical_record_mock)

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
