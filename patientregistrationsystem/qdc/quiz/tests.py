# -*- coding: UTF-8 -*-
from django.test import TestCase, Client

from django.http import Http404
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

import pyjsonrpc

from django.shortcuts import get_object_or_404
from django.test.client import RequestFactory
from django.contrib.auth.models import Group
from quiz.models import ClassificationOfDiseases, MedicalRecordData, Diagnosis, ComplementaryExam, ExamFile

from quiz.views import medical_record_view, medical_record_update, diagnosis_create, \
    medical_record_create_diagnosis_create, exam_create, exam_view, \
    Gender, Schooling, Patient, patient_update, patient, restore_patient, \
    User, reverse, user_update
from quiz.abc_search_engine import Questionnaires

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.http import int_to_base36
from quiz.models import UserProfile

from quiz.validation import CPF

import re

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


class FormUserValidation(TestCase):
    user = ''

    def setUp(self):
        """ Configura autenticacao e variaveis para iniciar cada teste """

        self.user = User.objects.create_superuser(username=USER_USERNAME, email='jenkins.neuromat@gmail.com',
                                                  password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.force_password_change = False
        profile.save()

        self.group = Group.objects.create(name='group')
        self.group.save()

        self.factory = RequestFactory()

        self.data = {'username': ['username'],
                     'first_name': ['General'],
                     'last_name': ['Test'],
                     'password': ['Adm!123'],
                     'password2': ['Adm!123'],
                     'groups': [self.group.id],
                     'email': ['email@test.com'],
                     'action': 'save'}

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def reset(self, user_added=None, request=None, domain_override=None,
              email_template_name='registration/password_reset_email.html',
              use_https=False, token_generator=default_token_generator):
        """Reset users password"""
        if not user_added.email:
            raise ValueError('Email address is required to send an email')

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        t = loader.get_template(email_template_name)
        c = {
            'email': user_added.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user_added.id),
            'user': user_added,
            'token': token_generator.make_token(user_added),
            'protocol': use_https and 'https' or 'http',
        }
        # send_mail(_("Your account for %s") % site_name, t.render(Context(c)), None, [user_added.email])
        subject_template_name = 'registration/password_reset_subject.txt'
        subject = loader.render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        # CHANGES START HERE!
        plain_text_content = loader.render_to_string(email_template_name.replace('with_html', 'plaintext'), c)
        html_content = loader.render_to_string(email_template_name, c)

        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives(subject, plain_text_content, 'jenkins.neuromat@gmail.com', [user_added.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def test_user_password_pattern(self):
        """Testa o pattern definido """
        # Detalhamento do pattern
        # (			# Start of group
        # (?=.*\d)		#   must contains one digit from 0-9
        # (?=.*[a-z])		#   must contains one lowercase characters
        # (?=.*[A-Z])		#   must contains one uppercase characters
        # (?=.*[@#$%])		#   must contains one special symbols in the list "@#$%"
        # .		#     match anything with previous condition checking
        # {6,20}	#        length at least 6 characters and maximum of 20
        # )
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = "abcC2@!$"

        self.assertTrue(self.confirm_password(pattern, password), True)

    def confirm_password(self, pattern, password):
        a = re.compile(pattern)
        return a.match(password)

    def test_user_invalid_username(self):
        """ Teste de inclusao de usuario com nome de usuario invalido"""

        self.data['username'] = ''

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)

        self.assertFormError(response, "form", "username", u'Este campo é obrigatório.')
        self.assertEqual(User.objects.filter(username='').count(), 0)

    def test_user_invalid_email(self):
        """
        Testa inclusao de usuario com sucesso
        """

        self.data['email'] = 'email@invalid.'

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertFormError(response, "form", "email", u'Informe um endereço de email válido.')
        self.assertEqual(User.objects.filter(username='').count(), 0)

    def test_user_passwords_doesnt_match(self):
        """
        Testa senhas não conferem
        """
        user_pwd = 'test_pwd'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc123'
        self.data['password2'] = 'acc123'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_valid_pattern(self):
        """
        Testa padrao valido de senha definido para o usuario
        """
        user_pwd = 'test_pwd_1'
        pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
        password = 'Abc$123'
        self.assertTrue(self.confirm_password(pattern=pattern, password=password), True)

        self.data['username'] = user_pwd
        self.data['password'] = password

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_invalid_pattern_abc(self):
        """
        Testa padrao invalido de senha definido para o usuario (senha: abc)
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_password_check_invalid_pattern_123(self):
        """
        Testa padrao invalido de senha definido para o usuario (senha: 123)
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = '123'

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_empty_password(self):
        """
        Testa senha em branco
        """
        user_pwd = 'test_pwd_2'
        self.data['username'] = user_pwd
        self.data['password'] = ''

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password", u'Este campo é obrigatório.')
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 0)

    def test_user_create(self):
        """
        Testa inclusao de usuario com sucesso
        """
        username = 'test_username'
        self.data['username'] = username

        response = self.client.post(reverse(USER_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

    def test_user_create_mail_password_define(self):
        """
        Testa inclusao de usuario com sucesso
        """
        username = 'test_username'
        self.data['email'] = 'romulojosefranco@gmail.com'
        self.data['username'] = username

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

        user_added = User.objects.filter(username=username).first()
        self.reset(user_added, request)

    def test_user_read(self):
        """
        Testa visualizar usuario
        """

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = user_update(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(USER_EDIT, args=[self.user.pk]), self.data)
        self.assertEqual(response.status_code, 302)

    def test_user_update_get(self):
        """
        Testa atualizar usuario - Metodo GET
        """

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = user_update(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)

    def test_user_update_post(self):
        """
        Testa atualizar usuario - Metodo POST
        """

        first_name = 'test_username'
        self.data['first_name'] = first_name

        response = self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(id=self.user.pk).count(), 1)

        user_first_name = User.objects.filter(id=self.user.pk).first()

        self.assertEqual(user_first_name.first_name, first_name)

    def test_user_remove(self):
        """
        Testa deletar usuario
        """
        user_str = 'user_remove'
        user_to_delete = User.objects.create_user(username=user_str, email='test@delete.com',
                                                  password='Del!123')
        user_to_delete.is_staff = True
        user_to_delete.is_superuser = True
        user_to_delete.is_active = True
        user_to_delete.save()
        self.assertEqual(User.objects.filter(username=user_str).count(), 1)

        self.data['action'] = 'remove'

        response = self.client.post(reverse('user_delete', args=(user_to_delete.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        user_to_delete = get_object_or_404(User, pk=user_to_delete.pk)
        self.assertEqual(user_to_delete.is_active, False)

        user_to_delete.is_active = True
        response = self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 403)
        user_to_delete = get_object_or_404(User, pk=user_to_delete.pk)
        self.assertEqual(user_to_delete.is_active, False)


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
        self.data[CPF_ID] = ''
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
            file_to_test = SimpleUploadedFile('quiz/exam_file.txt', 'rb')
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

        # Create a cids to make search.
        self.util.create_cid10_to_search()

        # Busca valida
        self.data['medical_record'] = ''
        self.data['patient_id'] = ''
        self.data[search_text_meta] = 'A'
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


# @unittest.skip("Don't want to test")
class ABCSearchEngineTest(TestCase):
    session_key = None
    server = None

    def setUp(self):
        self.server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        username = "jenkins"
        password = "numecusp"
        self.session_key = self.server.get_session_key(username, password)
        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        if isinstance(self.session_key, dict):
            if 'status' in self.session_key:
                self.assertNotEqual(self.session_key['status'], 'Invalid user name or password')
                print 'Failed to connect Lime Survey %s' % self.session_key['status']

    def test_complete_survey(self):
        lime_survey = Questionnaires()
        sid = None

        try:
            # Cria uma nova survey no lime survey
            title_survey = 'Questionario de teste'
            sid = lime_survey.add_survey(9999, title_survey, 'en', 'G')

            # Obtenho o titulo da survey
            survey_title = lime_survey.get_survey_title(sid)
            self.assertEqual(survey_title, title_survey)

            # Verifica se esta ativa
            survey_active = lime_survey.get_survey_properties(sid, 'active')
            self.assertEqual(survey_active, 'N')

            # Obtem uma propriedade - Administrador da Survey
            survey_admin = lime_survey.get_survey_properties(sid, 'admin')
            self.assertEqual(survey_admin, None)

            # Criar grupo de questoes
            group_id = lime_survey.add_group_questions(sid, "Group Question",
                                                       'Test for create group question on lime survey')

            handle_file_import = open('quiz/static/quiz/tests/limesurvey_groups.lsg', 'r')
            questions_data = handle_file_import.read()
            questions_id = lime_survey.insert_questions(sid, questions_data, 'lsg')
            self.assertGreaterEqual(questions_id, 1)

            # Inicia tabela de tokens
            status = lime_survey.activate_tokens(sid)
            self.assertEqual(status, 'OK')

            # Ativar survey
            status = lime_survey.activate_survey(sid)
            self.assertEqual(status, 'OK')

            # Verifica se esta ativa
            survey_active = lime_survey.get_survey_properties(sid, 'active')
            self.assertEqual(survey_active, 'Y')

            # Adiciona participante e obtem o token
            result_token = lime_survey.add_participant(sid, 'Teste', 'Django', 'teste@teste.com')

            # Verifica se o token
            token = lime_survey.get_participant_properties(sid, result_token, "token")
            self.assertEqual(token, result_token['token'])

        finally:
            # Deleta a survey gerada no Lime Survey
            status = lime_survey.delete_survey(sid)
            self.assertEqual(status, 'OK')

    def test_find_all_questionnaires_method_returns_correct_result(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_all_questionnaires(), list_survey)
        q.release_session_key()

    def test_find_questionnaire_by_id_method_found_survey(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_questionnaire_by_id(list_survey[3]['sid']), list_survey[3])
        q.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id('three'))
        q.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id(10000000))
        q.release_session_key()

    def test_list_active_questionnaires(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        list_active_survey = []
        for survey in list_survey:
            survey_has_token = q.survey_has_token_table(survey['sid'])
            if survey['active'] == "Y" and survey_has_token is True:
                list_active_survey.append(survey)
        self.assertEqual(q.find_all_active_questionnaires(), list_active_survey)
        q.release_session_key()

    def test_add_participant_to_a_survey(self):
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(
            sid, participant_data['firstname'], participant_data['lastname'], participant_data['email'])

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firsStname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['token_id']
        tokens_to_delete = []
        tokens_to_delete.append(token_id)

        # remover participante do questionario
        result = self.server.delete_participants(self.session_key, sid, [token_id])

        self.assertEqual(result[str(token_id)], 'Deleted')

        surveys.release_session_key()

    def test_add_and_delete_survey(self):
        """
        TDD - Criar uma survey de teste e apos devera ser excluida
        """
        survey_id_generated = self.server.add_survey(self.session_key, 9999, 'Questionario de Teste', 'en', 'G')
        self.assertGreaterEqual(survey_id_generated, 0)

        status = self.server.delete_survey(self.session_key, survey_id_generated)
        self.assertEqual(status['status'], 'OK')
        self.server.release_session_key(self.session_key)

    def test_add_and_delete_survey_methods(self):
        q = Questionnaires()
        sid = q.add_survey('9999', 'Questionario de Teste', 'en', 'G')
        self.assertGreaterEqual(sid, 0)

        status = q.delete_survey(sid)
        self.assertEqual(status, 'OK')

    # def test_get_survey_property_usetokens(self):
    # """testa a obtencao das propriedades de um questionario"""
    #
    # surveys = Questionnaires()
    # result = surveys.get_survey_properties(641729, "usetokens")
    # surveys.release_session_key()
    #
    # pass

    # def test_get_participant_property_usetokens(self):
    # """testa a obtencao das propriedades de um participant/token"""
    #
    # surveys = Questionnaires()
    #
    # # completo
    # result1 = surveys.get_participant_properties(426494, 2, "completed")
    #
    # # nao completo
    # result2 = surveys.get_participant_properties(426494, 230, "completed")
    # result3 = surveys.get_participant_properties(426494, 230, "token")
    # surveys.release_session_key()
    #
    # pass

    # def test_survey_has_token_table(self):
    # """testa se determinado questionario tem tabela de tokens criada"""
    #
    # surveys = Questionnaires()
    #
    #     # exemplo de "true"
    #     result = surveys.survey_has_token_table(426494)
    #
    #     # exemplo de "false"
    #     result2 = surveys.survey_has_token_table(642916)
    #     surveys.release_session_key()
    #
    #     pass

    def test_delete_participant_to_a_survey(self):
        """Remove survey participant test"""
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(
            sid, participant_data['firstname'], participant_data['lastname'], participant_data['email'])

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firstname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['token_id']
        tokens_to_delete = []
        tokens_to_delete.append(token_id)

        # remover participante do questionario
        result = surveys.delete_participant(sid, token_id)

        self.assertEqual(result[str(token_id)], 'Deleted')

        surveys.release_session_key()
