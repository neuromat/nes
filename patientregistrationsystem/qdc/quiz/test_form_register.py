# -*- coding: UTF-8 -*-
from django.test import TestCase, Client
from django.http import Http404
from django.test.client import RequestFactory
from datetime import date
from views import User, GenderOption, reverse, Patient, patient_update, patient, patients

PATIENT_NEW = 'patient_new'


class FormValidation(TestCase):
    user = ''
    data = {}

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        print "Setting User for start tests to", self._testMethodName
        username_dummy = 'myadmin'
        password_dummy = 'mypassword'

        self.user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=username_dummy, password=password_dummy)
        self.assertEqual(logged, True)

        self.gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        self.gender_opt.save()

        self.data = {'name_txt': 'Patient for test',
                     'cpf_id': '374.276.738-08',
                     'gender_opt': str(self.gender_opt.id),
                     'date_birth_txt': '01/02/1995',
                     'email_txt': 'email@email.com',
                     'currentTab': '0'}

    def test_invalid_cpf(self):
        """
        Testa inclusao de paciente com cpf invalido
        """

        # CPF invalido
        cpf = '100.913.651-81'
        self.data['cpf_id'] = cpf

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf_id", u'CPF ' + cpf + u' n\xe3o \xe9 v\xe1lido')

    def test_empty_cpf(self):
        """
        Testa inclusao de paciente com cpf invalido
        """

        # CPF vazio
        name = 'Patient-CPF-Vazio'
        self.data['name_txt'] = name
        self.data['cpf_id'] = ''

        response = self.client.post(reverse(PATIENT_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)


    def test_future_date_birth(self):
        """
        Testa inclusao de paciente com data de nascimento futura
        """
        name = 'test_future_date_birth'
        self.data['name_txt'] = name
        self.data['date_birth_txt'] = '15/05/2201'

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name_txt=name).count(), 0)

    def get_current_date(self):
        """
        Obtem a data atual no formato dd/mm/yyyy
        """
        d = date.today()
        d.isoformat()
        date_birth = d.strftime("%d/%m/%Y")
        return date_birth

    def test_date_birth_now(self):
        """
        Testa inclusao de paciente com data de nascimento futura
        """

        date_birth = self.get_current_date()
        name = 'test_date_birth_now'
        self.data['date_birth_txt'] = date_birth
        self.data['name_txt'] = name
        self.data['currentTab'] = 1

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)

    def test_patient_added(self):
        """
        Testa inclusao de paciente com campos obrigatorios
        """
        name = 'test_patient_added'
        self.data['name_txt'] = name

        try:
            self.client.post(reverse(PATIENT_NEW), self.data, follow=True)

            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)
        except Http404:
            pass

    def test_valid_email(self):
        """
        Teste de email invalido
        """

        self.data['email_txt'] = 'mail@invalid.'

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, 'Informe um endereço de email válido')

    def test_valid_name(self):
        """
        Teste de validacao do campo nome completo  - obrigatorio
        """

        self.data['name_txt'] = ''

        response = self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertContains(response, 'Nome não preenchido')



    def test_view_and_search_patient(self):
        """
        Teste de visualizacao de paciente apos cadastro na base de dados
        """

        p = Patient()

        p.name_txt = 'Paciente de teste'
        p.date_birth_txt = '2001-01-15'
        p.gender_opt_id = self.gender_opt.id
        p.save()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % p.pk)
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        try:
            response = patient(request, patient_id=p.pk)
            self.assertEqual(response.status_code, 200)

            self.data['search_text'] = 'Paciente'
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)

            self.data['search_text'] = '012'
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)


        except Http404:
            pass

    def test_patient_list(self):
        p = Patient()

        p.name_txt = 'Paciente de teste'
        p.date_birth_txt = '2001-01-15'
        p.gender_opt_id = self.gender_opt.id
        p.save()


        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%d' % p.pk)
        request.user = self.user

        try:
            response = patient(request, p.pk)
            self.assertEqual(response.status_code, 200)

        except Http404:
            pass

    def test_update_patient(self):
        """Teste de paciente existente na base de dados """

        p = Patient()

        p.name_txt = 'Paciente de teste UPDATE'
        p.date_birth_txt = '2001-01-15'
        p.gender_opt_id = self.gender_opt.id
        p.save()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % p.pk)
        request.user = self.user

        try:
            response = patient_update(request, patient_id=p.pk)
            self.assertEqual(response.status_code, 200)
            response = self.client.post(reverse('patient_edit', args=[p.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            self.data['remove'] = p.pk
            response = self.client.post(reverse('patient_edit', args=[p.pk]), self.data)
            self.assertEqual(response.status_code, 302)

        except Http404:
            pass

    def test_update_patient_not_exist(self):
        """Teste de paciente nao existente na base de dados """

        # p = Patient()
        #
        # p.name_txt = 'Paciente de teste UPDATE'
        # p.date_birth_txt = '2001-01-15'
        # p.gender_opt_id = self.gender_opt.id
        # p.save()
        id = 99999

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % id)
        request.user = self.user

        try:
            response = patient_update(request, patient_id=id)
            #self.assertRaises(response, 'DoesNotExist')
            self.assertEqual(response.status_code, 404)
        except Http404:
            pass

    def test_views(self):
        client = Client()
        self.assertEqual(client.get('/response').status_code, 404)
        self.assertEqual(client.get('/notfound').status_code, 404)
        self.assertEqual(client.get('/quiz/patient/999999/').status_code, 302)
        self.assertEqual(client.get('/error').status_code, 404)
        self.assertEqual(client.get('/redirect_response').status_code, 404)
        self.assertEqual(client.get('/redirect_notfound').status_code, 404)
        self.assertEqual(client.get('/redirect_redirect_response').status_code, 404)
        self.assertEqual(client.get('/quiz').status_code, 301)