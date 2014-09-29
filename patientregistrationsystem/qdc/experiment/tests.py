# coding=utf-8
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404

from experiment.models import Experiment, QuestionnaireConfiguration, TimeUnit, Subject, \
    QuestionnaireResponse, SubjectOfExperiment
from experiment.views import experiment_update, upload_file
from quiz.abc_search_engine import Questionnaires
from quiz.tests import UtilTests

from quiz.views import User

import datetime

LIME_SURVEY_TOKEN_ID_2 = 24

LIME_SURVEY_TOKEN_ID_1 = 7

EXPERIMENT_LIST = 'experiment_list'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'

SEARCH_TEXT = 'search_text'
SUBJECT_SEARCH = 'subject_search'

LIME_SURVEY_CODE_ID_TEST = 641729


class ExperimentTest(TestCase):
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

    def test_experiment_list(self):
        """
        Testa a listagem de experimentos
        """

        # lista experimentos
        response = self.client.get(reverse(EXPERIMENT_LIST))
        self.assertEqual(response.status_code, 200)

        # deve retornar vazia
        self.assertEqual(len(response.context['experiments']), 0)

        # crio experimento
        experiment = Experiment.objects.create(title="Experimento-1", description="Descricao do Experimento-1")
        experiment.save()

        # lista experimentos: deve retornar 1
        response = self.client.get(reverse(EXPERIMENT_LIST))
        self.assertEqual(response.status_code, 200)

        # deve retornar 1 experimento
        self.assertEqual(len(response.context['experiments']), 1)

    def test_experiment_create(self):
        """Testa a criacao de um experimento """

        # Abre tela de cadastro de experimento
        response = self.client.get(reverse('experiment_new'))
        self.assertEqual(response.status_code, 200)

        # Dados sobre o experimento
        self.data = {'action': ['save'], 'description': ['Experimento de Teste'], 'title': ['Teste Experimento']}

        # Obtem o total de experimentos existente na tabela
        count_before_insert = Experiment.objects.all().count()

        # Efetua a adicao do experimento
        response = self.client.post(reverse('experiment_new'), self.data)

        # Verifica se o status de retorno eh adequado
        self.assertEqual(response.status_code, 302)

        # Obtem o toal de experimento apos a inclusao
        count_after_insert = Experiment.objects.all().count()

        # Verifica se o experimento foi de fato adicionado
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_experiment_update(self):
        """Testa a atualizacao do experimento"""

        # Criar um experimento para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse('experiment_edit', args=[experiment.pk, ]))
        request.user = self.user

        try:
            response = experiment_update(request, experiment_id=experiment.pk)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

        # Efetua a atualizacao do experimento
        self.data = {'action': ['save'], 'description': ['Experimento de Teste'], 'title': ['Teste Experimento']}
        response = self.client.post(reverse('experiment_edit', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        count = Experiment.objects.all().count()

        # Remove experimento
        self.data = {'action': ['remove'], 'description': ['Experimento de Teste'], 'title': ['Teste Experimento']}
        response = self.client.post(reverse('experiment_edit', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experiment.objects.all().count(), count - 1)


class QuestionnaireConfigurationTest(TestCase):
    lime_survey = None

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

        # Conecta no Lime Survey
        self.lime_survey = Questionnaires()
        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        if isinstance(self.lime_survey.session_key, dict):
            if 'status' in self.lime_survey.session_key:
                self.assertNotEqual(self.lime_survey.session_key['status'], 'Invalid user name or password')
                print 'Failed to connect Lime Survey %s' % self.lime_survey.session_key['status']

    def test_questionnaire_create(self):
        """Testa a criacao de um questionario para um dado experimento"""

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        # Cria o TimeUnit para ser utilizado nos testes com intervalo de tempo
        time_unit = TimeUnit.objects.create(name='Horas')
        time_unit.save()

        # Abre tela de cadastro de questionario
        response = self.client.get(reverse('questionnaire_new', args=(experiment.pk,)))
        self.assertEqual(response.status_code, 200)

        sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            # Cria um questionario com os dados default apresentados em tela
            count_before_insert = QuestionnaireConfiguration.objects.all().count()
            self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': [sid]}
            response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
            self.assertEqual(response.status_code, 200)

            count_after_insert = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_insert, count_before_insert + 1)

            # Remove o questionario criado
            questionnaire_created = get_object_or_404(QuestionnaireConfiguration, experiment=experiment,
                                                      lime_survey_id=sid)
            if questionnaire_created:
                questionnaire_created.delete()

            # Criar um questionario com dados incompletos - Codigo Questionario invalido
            count_before_insert = QuestionnaireConfiguration.objects.all().count()
            self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': [0]}
            response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
            self.assertEqual(response.status_code, 200)

            # TODO Verificar este teste, esta permitindo codigo de questionario do Lime Survey invalido
            count_after_insert = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_insert,
                             count_before_insert + 1)

            # Criar um questionario com intervalo de preenchimento
            count_before_insert = QuestionnaireConfiguration.objects.all().count()
            self.data = {'interval_between_fills_value': ['12'],
                         'number_of_fills': ['3'],
                         'questionnaire_selected': [sid],
                         'interval_between_fills_unit': str(time_unit.pk),
                         'action': ['save']}

            response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
            self.assertEqual(response.status_code, 200)

            count_after_insert = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_insert, count_before_insert + 1)

        finally:
            # Deleta a survey gerada no Lime Survey
            status = self.lime_survey.delete_survey(sid)
            self.assertEqual(status, 'OK')

    def test_questionnaire_update(self):
        """ Teste atualizacao de um questionario """

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        # Cria uma survey no Lime Survey
        sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            # Cria um questionario
            questionnaire = QuestionnaireConfiguration.objects.create(lime_survey_id=sid, experiment=experiment,
                                                                      number_of_fills=2)
            questionnaire.save()

            # Cria o TimeUnit para ser utilizado nos testes com intervalo de tempo
            time_unit = TimeUnit.objects.create(name='Horas')
            time_unit.save()

            # Abre tela de cadastro de questionario
            response = self.client.get(reverse('questionnaire_edit', args=(questionnaire.pk,)))
            self.assertEqual(response.status_code, 200)

            # Conta o numero de questionarios existentes antes da atualizacao
            count_before_insert = QuestionnaireConfiguration.objects.all().count()

            # Prepara dados POST para atualizacao
            self.data = {'interval_between_fills_value': ['12'],
                         'number_of_fills': ['3'],
                         'questionnaire_selected': [sid],
                         'interval_between_fills_unit': str(time_unit.pk),
                         'action': ['save']}

            # Executa a operacao via metodo POST
            response = self.client.post(reverse('questionnaire_edit', args=(questionnaire.pk,)), self.data, follow=True)

            # Verifica se o retorno e valido
            self.assertEqual(response.status_code, 200)

            # Conta numero de questionarios existentes apos a atualizacao. Isso certifica que nao ira
            # gerar uma adicao ao inves de atualizacao do questionario
            count_after_insert = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_insert, count_before_insert)

            # Remove o questionario atualizado
            self.data = {'interval_between_fills_value': ['12'],
                         'number_of_fills': ['3'],
                         'questionnaire_selected': [sid],
                         'interval_between_fills_unit': str(time_unit.pk),
                         'action': ['remove']}

            response = self.client.post(reverse('questionnaire_edit', args=(questionnaire.pk,)), self.data, follow=True)
            self.assertEqual(response.status_code, 200)

            count_after_remove = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_remove, count_after_insert - 1)

        finally:
            # Deleta a survey gerada no Lime Survey
            status = self.lime_survey.delete_survey(sid)
            self.assertEqual(status, 'OK')


class SubjectTest(TestCase):
    util = UtilTests()

    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        print 'Set up for', self._testMethodName

        # self.user = User.objects.all().first()
        # if self.user:
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        # Conecta no Lime Survey
        self.lime_survey = Questionnaires()

        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        if isinstance(self.lime_survey.session_key, dict):
            if 'status' in self.lime_survey.session_key:
                self.assertNotEqual(self.lime_survey.session_key['status'], 'Invalid user name or password')
                print 'Failed to connect Lime Survey %s' % self.lime_survey.session_key['status']

    def test_subject_view_and_search(self):
        """
        Teste de visualizacao de paciente apos cadastro na base de dados
        """

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Teste",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        patient_mock = self.util.create_patient_mock(user=self.user)
        self.data = {SEARCH_TEXT: 'Pacient', 'experiment_id': experiment.id}

        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient_mock.name)
        self.assertEqual(response.context['patients'].count(), 1)

        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'].count(), 1)
        self.assertContains(response, patient_mock.cpf)

        self.data[SEARCH_TEXT] = ''
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'], '')

    def test_subject(self):
        """
        Teste
        """
        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        patient_mock = self.util.create_patient_mock(user=self.user)

        # Cria uma survey no Lime Survey
        sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            # Cria um questionario
            questionnaire = QuestionnaireConfiguration.objects.create(lime_survey_id=sid, experiment=experiment,
                                                                      number_of_fills=1)
            questionnaire.save()

            # Cria o TimeUnit para ser utilizado nos testes com intervalo de tempo
            time_unit = TimeUnit.objects.create(name='Horas')
            time_unit.save()

            # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
            response = self.client.get(reverse('subjects', args=(experiment.pk,)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['subject_list']), 0)

            count_before_insert_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            response = self.client.post(reverse('subject_insert', args=(experiment.pk, patient_mock.pk)))
            self.assertEqual(response.status_code, 302)
            count_after_insert_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            self.assertEqual(count_after_insert_subject, count_before_insert_subject + 1)

            # Reabre a tela de cadastro de participantes - devera conter ao menos um participante
            # cadastrado
            response = self.client.get(reverse('subjects', args=(experiment.pk,)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['subject_list']), 1)

            # Inserir participante ja inserido para o experimento
            count_before_insert_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            response = self.client.post(reverse('subject_insert', args=(experiment.pk, patient_mock.pk)))
            self.assertEqual(response.status_code, 302)
            count_after_insert_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            self.assertEqual(count_after_insert_subject, count_before_insert_subject)

            subject = Subject.objects.all().first()

            # Associar participante a Survey e iniciar preenchimento
            # Abrir a tela de associacao
            response = self.client.get(reverse('subject_questionnaire',
                                               args=[experiment.pk, subject.pk]))
            self.assertEqual(response.status_code, 200)

            # Prepara para o a associacao entre preenchimento da Survey,
            # participante e experimento
            response = self.client.get(reverse('subject_questionnaire_response',
                                               args=[experiment.pk, subject.pk, questionnaire.pk, ]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['creating'], True)

            # Dados para preenchimento da Survey
            self.data = {'date': ['29/08/2014'], 'action': ['save']}

            # Inicia o preenchimento de uma Survey sem tabela de tokens iniciada
            response = self.client.post(reverse('subject_questionnaire_response',
                                                args=[experiment.pk, subject.pk, questionnaire.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['FAIL'], False)

            # Inicia o preenchimento de uma Survey INATIVA
            response = self.client.post(reverse('subject_questionnaire_response',
                                                args=[experiment.pk, subject.pk, questionnaire.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['FAIL'], False)

            status = self.lime_survey.activate_tokens(sid)
            self.assertEqual(status, 'OK')

            # Ativar survey
            status = self.lime_survey.activate_survey(sid)
            self.assertEqual(status, 'OK')

            # Inicia o preenchimento de uma Survey NORMAL
            response = self.client.post(reverse('subject_questionnaire_response',
                                                args=[experiment.pk, subject.pk, questionnaire.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['FAIL'], True)

            questionnaire_response = QuestionnaireResponse.objects.all().first()

            # Acessa tela de atualizacao do preenchimento da Survey
            response = self.client.get(reverse('questionnaire_response_edit',
                                               args=[questionnaire_response.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['FAIL'], None)

            # Atualiza o preenchimento da survey
            response = self.client.post(reverse('questionnaire_response_edit',
                                                args=[questionnaire_response.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['FAIL'], True)

            response = self.client.get(reverse('questionnaire_response_edit',
                                               args=[questionnaire_response.pk, ]), self.data)
            self.assertEqual(response.status_code, 200)

            # Remove preenchimento da Survey
            count_before_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()

            self.data['action'] = 'remove'
            response = self.client.post(reverse('questionnaire_response_edit',
                                                args=[questionnaire_response.pk, ]), self.data)
            self.assertEqual(response.status_code, 302)

            count_after_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()
            self.assertEqual(count_before_delete_questionnaire_response - 1, count_after_delete_questionnaire_response)

            # Remover participante associado a survey
            self.data = {'action': 'remove'}
            count_before_delete_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            response = self.client.post(reverse('subject_questionnaire', args=(experiment.pk, subject.pk)),
                                        self.data)
            self.assertEqual(response.status_code, 302)
            count_after_delete_subject = SubjectOfExperiment.objects.all().filter(experiment=experiment).count()
            self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)

        finally:
            # Deleta a survey gerada no Lime Survey
            status = self.lime_survey.delete_survey(sid)
            self.assertEqual(status, 'OK')

    def test_questionaire_view(self):
        """ Testa a visualizacao completa do questionario respondido no Lime Survey"""

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Teste-View",
                                               description="Descricao do Experimento-View")
        experiment.save()

        # Criar um Subject para o experimento
        patient_mock = self.util.create_patient_mock(user=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_experiment = SubjectOfExperiment(subject=subject_mock, experiment=experiment)
        subject_experiment.save()

        experiment.subjectofexperiment_set.add(subject_experiment)
        experiment.save()

        # Cria um questionario
        questionnaire_configuration = QuestionnaireConfiguration(lime_survey_id=LIME_SURVEY_CODE_ID_TEST,
                                                                 experiment=experiment,
                                                                 number_of_fills=2)
        questionnaire_configuration.save()

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.questionnaire_configuration = questionnaire_configuration
        questionnaire_response.subject_of_experiment = subject_experiment
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Visualiza preenchimento da Survey
        response = self.client.get(reverse('questionnaire_response_view',
                                           args=[questionnaire_response.pk, ]))
        self.assertEqual(response.status_code, 200)

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.questionnaire_configuration = questionnaire_configuration
        questionnaire_response.subject_of_experiment = subject_experiment
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_2
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Visualiza preenchimento da Survey
        response = self.client.get(reverse('questionnaire_response_view',
                                           args=[questionnaire_response.pk, ]))
        self.assertEqual(response.status_code, 200)

        # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
        response = self.client.get(reverse('subjects', args=(experiment.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subject_list']), 1)

    def test_subject_upload_consent_file(self):
        """
        Testa o upload de arquivos que corresponde ao formulario de consentimento do participante no experimento
        """

        experiment = Experiment.objects.all().first()
        if not experiment:
            experiment = Experiment.objects.create(title="Experimento-Teste-Upload",
                                                   description="Descricao do Experimento-Upload")
            experiment.save()

        patient_mock = self.util.create_patient_mock(user=self.user)

        subject_mock = Subject.objects.all().first()

        if not subject_mock:
            subject_mock = Subject.objects.create(patient=patient_mock)
            subject_mock.patient = patient_mock
            subject_mock.save()

        self.assertEqual(get_object_or_404(Subject, pk=subject_mock.pk), subject_mock)

        subject_experiment = SubjectOfExperiment.objects.all().first()
        if not subject_experiment:
            subject_experiment = SubjectOfExperiment.objects.create(subject=subject_mock, experiment=experiment)

        subject_experiment.experiment = experiment
        subject_experiment.subject = subject_mock
        subject_experiment.save()

        experiment.subjectofexperiment_set.add(subject_experiment)
        experiment.save()

        self.assertEqual(get_object_or_404(Experiment, pk=experiment.pk), experiment)
        self.assertEqual(get_object_or_404(SubjectOfExperiment, subject=subject_mock, experiment=experiment),
                         subject_experiment)

        # Upload Consent_form
        # Simula click no icone de acesso a pagina de upload do arquivo
        request = self.factory.get(reverse('upload_file', args=[subject_mock.pk, experiment.pk, ]))
        request.user = self.user
        response = upload_file(request, subject_id=subject_mock.pk, experiment_id=experiment.pk)
        self.assertEqual(response.status_code, 200)

        # Anexar arquivo
        consent_form_file = SimpleUploadedFile('quiz/consent_form.txt', 'rb')
        self.data = {'action': 'upload', 'consent_form': consent_form_file}
        url = reverse('upload_file', args=[experiment.pk, subject_mock.pk])
        # request = self.factory.post(url, self.data)d
        # request.user = self.user
        # response = upload_file(request, subject_id=subject_mock.pk, experiment_id=experiment.pk)
        response = self.client.post(reverse('upload_file', args=[experiment.pk, subject_mock.pk, ]), self.data,
                                    follow=True)
        # print response.content
        self.assertEqual(response.status_code, 200)

        # Remover arquivo
        self.data = {'action': 'remove'}
        response = self.client.post(reverse('upload_file', args=[experiment.pk, subject_mock.pk, ]), self.data)
        self.assertEqual(response.status_code, 302)
