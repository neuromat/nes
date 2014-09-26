# -*- coding: UTF-8 -*-
from django.test import TestCase, Client
from django.http import Http404
from util_test import UtilTests
from django.test.client import RequestFactory
from datetime import date
from views import User, Gender, Schooling, reverse, Patient, patient_update, patient, restore_patient

ACTION = 'action'
CPF = 'cpf'
SEARCH_TEXT = 'search_text'

PATIENT_SEARCH = 'patient_search'
PATIENT_VIEW = 'patient_view'
PATIENT_NEW = 'patient_new'
PATIENT_EDIT = 'patient_edit'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class PatientFormValidation(TestCase):
    user = ''
    data = {}
    util = UtilTests()

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        #print 'Set up for', self._testMethodName

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
        self.data[CPF] = ''

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

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def test_patient_create(self):
        """
        Testa inclusao de paciente com campos obrigatorios
        """
        name = self._testMethodName
        self.data['name'] = name

        self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

        self.data['currentTab'] = 0
        self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)

    def fill_social_demographic_data(self):
        """ Criar uma opcao de Schooling """

        school = Schooling.objects.create(name='Fundamental Completo')
        school.save()

        self.data['house_maid'] = '0'
        self.data['religion'] = '',
        self.data['amount_cigarettes'] = ''
        self.data['dvd'] = '1'
        self.data['wash_machine'] = '1'
        self.data['refrigerator'] = '1'
        self.data['alcohol_frequency'] = ''
        self.data['schooling'] = school.pk
        self.data['freezer'] = '0'
        self.data['tv'] = '1'
        self.data['bath'] = '1'
        self.data['radio'] = '1'
        self.data['automobile'] = '1'

    def test_patient_social_demographic_data(self):
        """
        Testa a inclusao de paciente com campos obrigatorios e dados sociais preenchidos
        """
        name = self._testMethodName
        self.data['name'] = name
        self.fill_social_demographic_data()

        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, u'Classe Social não calculada')

        patient_to_update = Patient.objects.filter(name=name).first()

        response = self.client.post(
            reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertNotContains(response, u'Classe Social não calculada')

        self.data.pop('wash_machine')
        name = 'test_patient_social_demographic_data_1'
        self.data['name'] = name
        self.data[CPF] = ''
        response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
        self.assertEqual(Patient.objects.filter(name=name).count(), 1)
        self.assertContains(response, u'Classe Social não calculada')

    def test_patient_valid_email(self):
        """
        Teste de email invalido
        """

        self.data['email'] = 'mail@invalid.'

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, 'Informe um endereço de email válido')

    def test_patient_valid_name(self):
        """
        Teste de validacao do campo nome completo  - obrigatorio
        """

        self.data['name'] = ''

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
        response = patient(request, patient_id=patient_mock.pk)
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

        response = patient(request, patient_mock.pk)
        self.assertEqual(response.status_code, 200)

    def test_patient_update_and_remove(self):
        """Teste de paciente existente na base de dados """

        patient_mock = self.util.create_patient_mock(name='Pacient Test Update', user=self.user)

        # Create an instance of a GET request.
        request = self.factory.get(reverse(PATIENT_VIEW, args=[patient_mock.pk]))
        request.user = self.user

        response = patient_update(request, patient_id=patient_mock.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data['currentTab'] = 0
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data[CPF] = ''
        response = self.client.post(reverse(PATIENT_EDIT, args=[patient_mock.pk]), self.data)
        self.assertEqual(response.status_code, 302)

        self.data[CPF] = patient_mock.cpf
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
        self.assertEqual(client.get('/quiz/patient/999999/').status_code, 302)
        self.assertEqual(client.get('/error').status_code, 404)
        self.assertEqual(client.get('/redirect_response').status_code, 404)
        self.assertEqual(client.get('/redirect_notfound').status_code, 404)
        self.assertEqual(client.get('/redirect_redirect_response').status_code, 404)
        self.assertEqual(client.get('/quiz').status_code, 301)

    def test_patient_verify_homonym(self):
        """  Testar a busca por homonimo """
        patient_mock = self.util.create_patient_mock(user=self.user)

        # Busca valida
        self.data[SEARCH_TEXT] = patient_mock.name
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

        self.data[SEARCH_TEXT] = patient_mock.cpf
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

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
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        self.data[SEARCH_TEXT] = patient_mock.cpf
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

