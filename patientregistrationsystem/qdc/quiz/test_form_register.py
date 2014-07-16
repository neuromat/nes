# -*- coding: UTF-8 -*-
from django.test import TestCase, Client
from django.http import Http404
from django.test.client import RequestFactory
from datetime import date
from models import ClassificationOfDiseases, MedicalRecordData, PainLocalization
from views import User, GenderOption, SchoolingOption, reverse, Patient, patient_update, patient, restore_patient

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
                     'email_txt': 'email@email.com'
        }

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
        name = 'Patient-CPF-Empty'
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

        self.client.post(reverse(PATIENT_NEW), self.data)

        self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)

    def test_patient_create(self):
        """
        Testa inclusao de paciente com campos obrigatorios
        """
        name = 'test_patient_create'
        self.data['name_txt'] = name

        try:
            self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)

            self.data['currentTab'] = 0
            self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)
        except Http404:
            pass

    def test_patient_with_medical_record(self):
        """
        Testa inclusao de paciente com campos obrigatorios
        """
        patient_mock = self.create_patient_mock(name='test_patient_with_medical_record')

        try:
            self.fill_medical_record()
            url = reverse("medical_record_new", args=(patient_mock.pk,))
            response = self.client.post(url, self.data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(MedicalRecordData.objects.filter(patient=patient_mock).count(), 1)

        except Http404:
            pass

    def fill_medical_record(self):
        pain_localization = PainLocalization.objects.create(pain_localization='pain')
        pain_localization.save()

        self.data['inferior_members_fracture_side'] = ''
        self.data['hormonal_dysfunction'] = '0'
        self.data['pelvis_fracture_side'] = ''
        self.data['scapula_fracture_side'] = ''
        self.data['pain_localizations'] = pain_localization.pk
        self.data['clavicle_fracture_side'] = ''
        self.data['fracture_history'] = '0'
        self.data['clavicle_surgery_side'] = ''
        self.data['inferior_members_surgery_side'] = ''
        self.data['pelvis_surgery_side'] = ''
        self.data['superior_members_surgery_side'] = ''
        self.data['hypertension'] = '0'
        self.data['scapula_surgery_side'] = ''
        self.data['vertigo_history'] = '0'
        self.data['nerve_surgery_type'] = ''
        self.data['nerve_surgery'] = '0'
        self.data['diabetes'] = '0'
        self.data['superior_members_fracture_side'] = ''
        self.data['headache'] = '1'

    def fill_social_demographic_data(self):
        # Criar uma opcao de Schooling
        school_opt = SchoolingOption.objects.create(schooling_txt='Fundamental Completo')
        school_opt.save()

        self.data['house_maid_opt'] = '0'
        self.data['religion_opt'] = '',
        self.data['amount_cigarettes_opt'] = ''
        self.data['dvd_opt'] = '1'
        self.data['wash_machine_opt'] = '1'
        self.data['refrigerator_opt'] = '1'
        self.data['alcohol_frequency_opt'] = ''
        self.data['schooling_opt'] = school_opt.pk
        self.data['freezer_opt'] = '0'
        self.data['tv_opt'] = '1'
        self.data['bath_opt'] = '1'
        self.data['radio_opt'] = '1'
        self.data['automobile_opt'] = '1'

    def test_patient_social_demographic_data(self):
        """
        Testa a inclusao de paciente com campos obrigatorios e dados sociais preenchidos
        """
        name = 'test_patient_social_demographic_data'
        self.data['name_txt'] = name
        self.fill_social_demographic_data()

        try:
            response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)
            self.assertNotContains(response, u'Classe Social não calculada')

            patient_to_update = Patient.objects.filter(name_txt=name).first()

            response = self.client.post(
                reverse('patient_edit', args=(patient_to_update.pk,)), self.data, follow=True)
            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)
            self.assertNotContains(response, u'Classe Social não calculada')

            self.data.pop('wash_machine_opt')
            name = 'test_patient_social_demographic_data_1'
            self.data['name_txt'] = name
            self.data['cpf_id'] = ''
            response = self.client.post(reverse(PATIENT_NEW), self.data, follow=True)
            self.assertEqual(Patient.objects.filter(name_txt=name).count(), 1)
            self.assertContains(response, u'Classe Social não calculada')

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

    def create_patient_mock(self, name='Pacient Test'):
        p_mock = Patient()
        p_mock.name_txt = name
        p_mock.date_birth_txt = '2001-01-15'
        p_mock.cpf_id = '374.276.738-08'
        p_mock.gender_opt_id = self.gender_opt.id
        p_mock.save()
        return p_mock

    def test_view_and_search_patient(self):
        """
        Teste de visualizacao de paciente apos cadastro na base de dados
        """

        patient_mock = self.create_patient_mock()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % patient_mock.pk)
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        try:
            response = patient(request, patient_id=patient_mock.pk)
            self.assertEqual(response.status_code, 200)

            self.data['search_text'] = 'Pacient'
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Pacient Test')
            self.assertEqual(response.context['patients'].count(), 1)

            self.data['search_text'] = 374
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['patients'].count(), 1)
            self.assertContains(response, '374.276.738-08')

            self.data['search_text'] = ''
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['patients'], '')

        except Http404:
            pass

    def test_patient_list(self):
        patient_mock = self.create_patient_mock()

        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%d' % patient_mock.pk)
        request.user = self.user

        try:
            response = patient(request, patient_mock.pk)
            self.assertEqual(response.status_code, 200)

        except Http404:
            pass

    def test_update_and_remove_patient(self):
        """Teste de paciente existente na base de dados """

        patient_mock = self.create_patient_mock(name='Pacient Test Update')

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % patient_mock.pk)
        request.user = self.user

        try:

            response = patient_update(request, patient_id=patient_mock.pk)
            self.assertEqual(response.status_code, 200)
            response = self.client.post(reverse('patient_edit', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            self.data['currentTab'] = 0
            response = self.client.post(reverse('patient_edit', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            self.data['cpf_id'] = ''
            response = self.client.post(reverse('patient_edit', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            self.data['cpf_id'] = '374.276.738-08'
            response = self.client.post(reverse('patient_edit', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            # Inicio do CPF inserido no self.data para retorno positivo na busca
            self.data['search_text'] = 374
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '374.276.738')

            self.data['action'] = 'remove'
            response = self.client.post(reverse('patient_view', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            self.data['action'] = 'not'
            response = self.client.post(reverse('patient_view', args=[patient_mock.pk]), self.data)
            self.assertEqual(response.status_code, 302)

            patient_removed = Patient.objects.get(pk=patient_mock.pk)
            self.assertEqual(patient_removed.removed, True)

            # Inicio do CPF inserido no self.data - nao eh pra haver retorno para este inicio de CPF
            self.data['search_text'] = 374
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, '374.276.738')

        except Http404:
            pass

    def test_update_patient_not_exist(self):
        """Teste de paciente nao existente na base de dados """

        # ID de paciente nao existente na base
        id_patient = 99999

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % id_patient)
        request.user = self.user

        try:
            response = patient_update(request, patient_id=id_patient)
            self.assertEqual(response.status_code, 404)
        except Http404:
            pass

    def test_patient_restore(self):
        """Teste de paciente recuperar paciente removido """

        # Cria um paciente ja removido no BD
        patient_mock = self.create_patient_mock()
        patient_mock.removed = True
        patient_mock.save()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/patient/%i/' % patient_mock.pk)
        request.user = self.user

        try:
            self.data['search_text'] = 374
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, '374.276.738')

            response = restore_patient(request, patient_id=patient_mock.pk)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Patient.objects.filter(name_txt=patient_mock.name_txt).exclude(removed=True).count(), 1)

            self.data['search_text'] = 374
            response = self.client.post(reverse('patient_search'), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '374.276.738')

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

    def test_cid_search(self):
        cid10 = ClassificationOfDiseases.objects.create(code='A01', description='Febres paratifoide',
                                                        abbreviated_description='A01 Febres paratifoide')
        cid10.save()
        cid10 = ClassificationOfDiseases.objects.create(code='B01', description='Febres tifoide ',
                                                        abbreviated_description='B01 Febres tifoide ')
        cid10.save()

        # Busca valida
        self.data['medical_record'] = ''
        self.data['patient_id'] = ''
        self.data['search_text'] = 'A'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paratifoide')

        self.data['search_text'] = 'B'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tifoide')

        self.data['search_text'] = '01'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Febres')
        self.assertEqual(response.context['cid_10_list'].count(), 2)

        # Busca invalida
        self.data['search_text'] = 'ZZZA1'
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'].count(), 0)

        self.data['search_text'] = ''
        response = self.client.post(reverse('cid10_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cid_10_list'], '')

    def test_patient_verify_homonym(self):
        patient_mock = self.create_patient_mock()

        # Busca valida
        self.data['search_text'] = patient_mock.name_txt
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

        self.data['search_text'] = patient_mock.cpf_id
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 0)
        self.assertEqual(response.context['patient_homonym'].count(), 1)

        self.data['search_text'] = ''
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'], '')

        # Busca invalida
        self.data['search_text'] = '!@#'
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        patient_mock.removed = True
        patient_mock.save()

        self.data['search_text'] = patient_mock.name_txt

        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)
        self.assertEqual(response.context['patient_homonym'].count(), 0)

        self.data['search_text'] = patient_mock.cpf_id
        response = self.client.post(reverse('patients_verify_homonym'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patient_homonym_excluded'].count(), 1)
        self.assertEqual(response.context['patient_homonym'].count(), 0)