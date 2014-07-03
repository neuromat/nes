# -*- coding: UTF-8 -*-
from django.test import TestCase, Client

from django.contrib.auth.models import *
from django.http import QueryDict, Http404
from django.test.client import RequestFactory
from datetime import date
from views import *

from django.utils.encoding import force_text


class FormValidation(TestCase):
    user = ''

    def setUp(self):
        print "Setting User for start tests to", self._testMethodName
        username_dummy = 'myadmin'
        password_dummy = 'mypassword'

        self.user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
        self.user.is_staff = True
        self.user.save()

        self.gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        self.gender_opt.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=username_dummy, password=password_dummy)
        self.assertEqual(logged, True)


    def test_invalid_cpf(self):
        """testa inclusao de paciente com cpf invalido"""

        data = {'name_txt': 'Novo paciente',
                'cpf_id': '100.913.651-81',
                'gender_opt': [str(self.gender_opt.id)]}

        response = self.client.post('/quiz/patient/new/', data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "patient_form", "cpf_id", u'CPF 100.913.651-81 n\xe3o \xe9 v\xe1lido')

    def test_invalid(self):
        """testa inclusao de paciente com cpf invalido"""

        data = "name_txt=Paciente&cpf_id=374.276.738-08&date_birth_txt=15/14/2001&gender_opt=1"

        response = self.client.post('/quiz/patient/new/', QueryDict(data))

        self.assertContains(response, 'Informe uma data válida.')

    def test_future_date_birth(self):
        """Testa inclusao de paciente com data de nascimento futura"""

        data = "name_txt=test_future_date_birth&cpf_id=374.276.738-08&date_birth_txt=15/05/2201&gender_opt=" + str(
            self.gender_opt.id) + "&currentTab=0"

        response = self.client.post('/quiz/patient/new/', QueryDict(data))

        self.assertEqual(Patient.objects.filter(name_txt='test_future_date_birth').count(), 1)

    def test_date_birth_now(self):
        """Testa inclusao de paciente com data de nascimento futura """

        d = date.today()
        d.isoformat()
        date_birth = d.strftime("%d/%m/%Y")
        data = "name_txt=test_date_birth_now&cpf_id=374.276.738-08&date_birth_txt=" + date_birth + "&gender_opt=1&currentTab=0"

        response = self.client.post('/quiz/patient/new/', QueryDict(data))

        self.assertEqual(Patient.objects.filter(name_txt='test_date_birth_now').count(), 1)


    def test_patient_added(self):
        """Testa inclusao de paciente com campos obrigatorios"""

        data = "name_txt=test_patient_added&date_birth_txt=15/11/1995&gender_opt=" + str(self.gender_opt.id)

        try:
            response = self.client.post('/quiz/patient/new/', QueryDict(data), follow=True)

            self.assertEqual(Patient.objects.filter(name_txt='test_patient_added').count(), 1)
        except Http404:
            pass

    def test_patient_add_ok(self):
        """Testa inclusao de paciente com sucesso"""

        data = {u'cpf_id': [u'248.215.628-98'], u'religion_opt': [u''], u'amount_cigarettes_opt': [u''],
                u'zipcode_number': [u'37704206'], u'state_txt': [u'RJ'], u'alcohol_frequency_opt': [u''],
                u'schooling_opt': [u''], u'street_txt': [u''], u'flesh_tone_opt': [u''], u'occupation_txt': [u''],
                u'medical_record_number': [u''],
                u'phone_number': [u'1'], u'marital_status_opt': [u''], u'rg_id': [u''], u'alcohol_period_opt': [u''],
                u'gender_opt': [str(self.gender_opt.id)], u'citizenship_txt': [u'BR'], u'payment_opt': [u''],
                u'name_txt': [u'Paciente de Teste'], u'email_txt': [u''], u'cellphone_number': [u''],
                u'date_birth_txt': [u'15/01/2003'], u'natural_of_txt': [u''], u'country_txt': [u'BR'],
                u'profession_txt': [u''], u'city_txt': [u'']}

        response = self.client.post('/quiz/patient/new/', data)
        # self.assertRedirects(response, '/quiz/patient/edit/1/?currentTab=0')
        self.assertEqual(Patient.objects.filter(cpf_id='248.215.628-98').count(), 1)

    def test_valid_email(self):
        """Teste de email invalido"""

        data = "name_txt=Paciente&cpf_id=374.276.738-08&email_txt=mail@invalid.&date_birth_txt=01/01/2000"

        response = self.client.post('/quiz/patient/new/', QueryDict(data))

        self.assertContains(response, 'Informe um endereço de email válido')


    def test_valid_name(self):
        """Teste de validacao do campo nome completo  - obrigatorio"""

        data = "name_txt=&cpf_id=374.276.738-08&date_birth_txt=01/01/2000"

        response = self.client.post('/quiz/patient/new/', QueryDict(data))

        self.assertContains(response, 'Nome não preenchido')

    def test_view_patient(self):
        """Teste de visualizacao de paciente apos cadastro na base de dados """

        p = Patient()

        p.name_txt = 'Paciente de teste'
        p.date_birth_txt = '2001-01-15'
        p.gender_opt_id = self.gender_opt.id
        p.save()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % p.pk)
        request.user = self.user

        # Test my_view() as if it were deployed at /customer/details
        try:
            response = patient(request, patient_id=p.pk)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

    def test_update_patient(self):
        """Teste de paciente nao existente na base de dados """

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






