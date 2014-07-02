# -*- coding: UTF-8 -*-
from django.test import TestCase
from django.contrib.auth.models import *
from models import GenderOption

from django.http import QueryDict


class FormValidation(TestCase):
    def setUp(self):
        print "Setting User for start tests to", self._testMethodName
        username_dummy = 'myadmin'
        password_dummy = 'mypassword'

        user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
        user.is_staff = True
        user.save()

        logged = self.client.login(username=username_dummy, password=password_dummy)
        self.assertEqual(logged, True)


    # def test_invalid_cpf(self):
    #     """testa inclusao de paciente com cpf invalido"""
    #
    #     # username_dummy = 'myadmin'
    #     # password_dummy = 'mypassword'
    #     #
    #     # user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
    #     # user.is_staff = True
    #     # user.save()
    #     #
    #     # logged = self.client.login(username=username_dummy, password=password_dummy)
    #     # self.assertEqual(logged, True)
    #
    #     data = {'name_txt': 'Novo paciente',
    #             'cpf_id': '100.913.651-81',
    #             'gender_opt': '1'}
    #     response = self.client.post('/quiz/patient/new/', data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFormError(response, "patient_form", "cpf_id", u'CPF 100.913.651-81 n\xe3o \xe9 v\xe1lido')
    #
    # def test_invalid(self):
    #     """testa inclusao de paciente com cpf invalido"""
    #
    #     # username_dummy = 'myadmin'
    #     # password_dummy = 'mypassword'
    #     #
    #     # user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
    #     # user.is_staff = True
    #     # user.save()
    #     #
    #     # logged = self.client.login(username=username_dummy, password=password_dummy)
    #     # self.assertEqual(logged, True)
    #
    #     data = {'name_txt': 'Novo paciente bom', 'cpf_id': '288.666.827-30', 'date_birth_txt': '01/01/2002',
    #             'gender_opt': '1'}
    #     response = self.client.post('/quiz/patient/new/', data)
    #     self.assertEqual(response.status_code, 200)
    #     # self.assertFormError(response, "patient_form", "cpf_id", u'CPF 100.913.651-81 n\xe3o \xe9 v\xe1lido')


    def test_patient_add_ok(self):
        """testa inclusao de paciente com sucesso"""

        # data = {u'name_txt': u'Paciente de Teste', u'cpf_id': u'374.276.738-08', u'gender_opt': u'2', u'date_birth_txt': u'01/01/2000'}

        # create GenderOption
        gender_opt = GenderOption.objects.create(gender_txt='Masculino')

        data = {u'cpf_id': [u'248.215.628-98'], u'religion_opt': [u''], u'amount_cigarettes_opt': [u''],
                u'zipcode_number': [u''], u'state_txt': [u'RJ'], u'alcohol_frequency_opt': [u''],
                u'schooling_opt': [u''], u'street_txt': [u''], u'flesh_tone_opt': [u''], u'occupation_txt': [u''],
                u'medical_record_number': [u''],
                u'phone_number': [u'1'], u'marital_status_opt': [u''], u'rg_id': [u''], u'alcohol_period_opt': [u''],
                u'citizenship_txt': [u'BR'], u'payment_opt': [u''],
                u'name_txt': [u'Paciente de Teste'], u'email_txt': [u''], u'cellphone_number': [u''],
                u'date_birth_txt': [u'15/01/2003'], u'natural_of_txt': [u''], u'country_txt': [u'BR'],
                u'profession_txt': [u''], u'city_txt': [u''],
                u'gender_opt': [str(gender_opt.id)]}


        response = self.client.post('/quiz/patient/new/', data)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(self, response, response.content, u'Paciente gravado com sucesso', html=True)
        # self.assertContains(response, u'Paciente gravado com sucesso', html=True)
        errors = response.context['patient_form'].errors
        self.assertEqual(0, len(errors), msg='Erros encontrados durante as validacoes: %s' % errors)
        messages = response.context['messages']
        print messages


    # def test_valid_email(self):
    #     """Teste de email invalido"""
    #
    #     # username_dummy = 'myadmin'
    #     # password_dummy = 'mypassword'
    #     #
    #     # user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
    #     # user.is_staff = True
    #     # user.save()
    #     #
    #     # logged = self.client.login(username=username_dummy, password=password_dummy)
    #     # self.assertEqual(logged, True)
    #
    #     data = "name_txt=Paciente&cpf_id=374.276.738-08&email_txt=mail@invalid.&date_birth_txt=01/01/2000"
    #
    #     response = self.client.post('/quiz/patient/new/', QueryDict(data))
    #
    #     errors = response.context['patient_form'].errors
    #
    #     # self.assertEqual(0, len(errors), msg='Erros encontrados durante as validacoes: %s' % errors)
    #
    #     # messages = response.context['messages']
    #     # print messages
    #     self.assertContains(response, 'Informe um endereço de email válido')
    #
    #
    # def test_valid_name(self):
    #     """Teste de validacao do campo nome completo  - obrigatorio"""
    #
    #     # username_dummy = 'myadmin'
    #     # password_dummy = 'mypassword'
    #     #
    #     # user = User.objects.create_user(username=username_dummy, email='test@dummy.com', password=password_dummy)
    #     # user.is_staff = True
    #     # user.save()
    #     #
    #     # logged = self.client.login(username=username_dummy, password=password_dummy)
    #     # self.assertEqual(logged, True)
    #
    #     data = "name_txt=&cpf_id=374.276.738-08&date_birth_txt=01/01/2000"
    #
    #     response = self.client.post('/quiz/patient/new/', QueryDict(data))
    #
    #     errors = response.context['patient_form'].errors
    #
    #     self.assertContains(response, 'Nome não preenchido')
    #     # self.assertEqual(0, len(errors), msg='Erros encontrados durante as validacoes: %s' % errors)
    #
    #     # messages = response.context['messages']
    #     # print messages