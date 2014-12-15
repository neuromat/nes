# coding=utf-8
import datetime

from django.http import Http404
from django.template.defaultfilters import title
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from django.shortcuts import get_object_or_404
import pyjsonrpc

from experiment.models import Experiment, Group, QuestionnaireConfiguration, TimeUnit, Subject, \
    QuestionnaireResponse, SubjectOfGroup, Sequence, ComponentConfiguration
from patient.models import ClassificationOfDiseases
from experiment.views import experiment_update, upload_file
from experiment.abc_search_engine import Questionnaires
from patient.tests import UtilTests
from custom_user.views import User


LIME_SURVEY_TOKEN_ID_2 = 2 # 24

LIME_SURVEY_TOKEN_ID_1 = 1 # 2

EXPERIMENT_LIST = 'experiment_list'
CLASSIFICATION_OF_DISEASES_CREATE = 'classification_of_diseases_insert'
CLASSIFICATION_OF_DISEASES_DELETE = 'classification_of_diseases_remove'
EXPERIMENT_NEW = 'experiment_new'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'

SEARCH_TEXT = 'search_text'
SUBJECT_SEARCH = 'subject_search'

# LIME_SURVEY_CODE_ID_TEST = 641729
LIME_SURVEY_CODE_ID_TEST = 953591


class ComponentConfigurationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def component_configuration_create(self):
        experiment = Experiment.objects.create(title="Experiment_title", description="Experiment_description")
        experiment.save()
        self.assertEqual(Experiment.objects.count(), 1)
        component = Sequence.objects.create(
            has_random_components=False,
            identification='Sequence_identification',
            description='Sequence_description',
            experiment=experiment,
            component_type='sequence'
        )
        component.save()
        self.assertEqual(Sequence.objects.count(), 1)
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration_name',
            component=component
        )
        component_configuration.save()
        self.assertEqual(ComponentConfiguration.objects.count(), 1)
        self.assertEqual(component_configuration.order, 1)

    def sequence_component_update_remove(self):
        # TODO terminar a remoção do component sequence através da view sequence_component_update
        experiment = Experiment.objects.create(title="Experiment_title", description="Experiment_description")
        experiment.save()
        self.assertEqual(Experiment.objects.count(), 1)
        component = Sequence.objects.create(
            has_random_components=False,
            identification='Sequence_identification',
            description='Sequence_description',
            experiment=experiment,
            component_type='sequence'
        )
        component.save()
        self.assertEqual(Sequence.objects.count(), 1)
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration_name',
            component=component
        )
        component_configuration.save()
        self.assertEqual(ComponentConfiguration.objects.count(), 1)
        self.assertEqual(component_configuration.order, 1)


class ClassificationOfDiseasesTest(TestCase):
    def setUp(self):
        """
        Configura autenticação e ambiente para testar a inclusão e remoção de um ClassificationOfDiseases em um Group de
         um Experiment

        """
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def classification_of_diseases_insert(self):
        """
        Testa a view classification_of_diseases_insert
        """
        # Crinando instancia de Experiment
        experiment = Experiment.objects.create(title="Experimento-1", description="Descricao do Experimento-1")
        experiment.save()

        # Criando instancia de Group
        group = Group.objects.create(experiment=experiment, title="Group-1", description="Descrição do Group-1")
        group.save()

        # Criando instancia de ClassificationOfDiseases
        classification_of_diseases = ClassificationOfDiseases.objects.create(code="1", description="test",
                                                                             abbreviated_description="t")
        # Inserindo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_CREATE, args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 1)

    def classification_of_diseases_remove(self):
        """
        Testa a view classification_of_diseases_insert
        """
        # Crinando instancia de Experiment
        experiment = Experiment.objects.create(title="Experimento-1", description="Descricao do Experimento-1")
        experiment.save()

        # Criando instancia de Group
        group = Group.objects.create(experiment=experiment, title="Group-1", description="Descrição do Group-1")
        group.save()

        # Criando instancia de ClassificationOfDiseases
        classification_of_diseases = ClassificationOfDiseases.objects.create(code="1", description="test",
                                                                             abbreviated_description="t")
        # Inserindo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_CREATE,
                                           args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 1)

        # Removendo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_DELETE,
                                           args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 0)


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

        # Criar um grupo mock para ser utilizado no teste
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Descricao do Group-update")
        group.save()

        # Abre tela de cadastro de questionario
        response = self.client.get(reverse('questionnaire_new', args=(group.pk,)))
        self.assertEqual(response.status_code, 200)

        sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            # Cria um questionario com os dados default apresentados em tela
            count_before_insert = QuestionnaireConfiguration.objects.all().count()
            self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': [sid]}
            response = self.client.post(reverse('questionnaire_new', args=(group.pk,)), self.data, follow=True)
            self.assertEqual(response.status_code, 200)

            count_after_insert = QuestionnaireConfiguration.objects.all().count()
            self.assertEqual(count_after_insert, count_before_insert + 1)

            # Remove o questionario criado
            questionnaire_created = get_object_or_404(QuestionnaireConfiguration, group=group,
                                                      lime_survey_id=sid)
            if questionnaire_created:
                questionnaire_created.delete()

            # Criar um questionario com dados incompletos - Codigo Questionario invalido
            count_before_insert = QuestionnaireConfiguration.objects.all().count()
            self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': [0]}
            response = self.client.post(reverse('questionnaire_new', args=(group.pk,)), self.data, follow=True)
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

            response = self.client.post(reverse('questionnaire_new', args=(group.pk,)), self.data, follow=True)
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

        # Criar um grupo mock para ser utilizado no teste
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Descricao do Group-update")

        # Cria uma survey no Lime Survey
        sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            # Cria um questionario
            questionnaire = QuestionnaireConfiguration.objects.create(lime_survey_id=sid, group=group,
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

        # Criar um grupo mock para ser utilizado no teste
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Descricao do Group-update")

        patient_mock = self.util.create_patient_mock(user=self.user)
        self.data = {SEARCH_TEXT: 'Pacient', 'experiment_id': experiment.id, 'group_id': group.id}

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


    # TODO: Reescrever este teste.
    # Este teste nao tem funcionado desde que começamos a validar se o questionario do limesurvey
    # tem os campos obrigatorios. A solucao seria deixar criado um questionario com os campos obrigatorios
    # e, antes de começar a testar, remover todos os tokens e deixa-lo como inativo
    # def test_subject(self):
    #     """
    #     Teste
    #     """
    #     # Criar um experimento mock para ser utilizado no teste
    #     experiment = Experiment.objects.create(title="Experimento-Update",
    #                                            description="Descricao do Experimento-Update")
    #     experiment.save()
    #
    #     # Criar um grupo mock para ser utilizado no teste
    #     group = Group.objects.create(experiment=experiment,
    #                                  title="Group-update",
    #                                  description="Descricao do Group-update")
    #     group.save()
    #
    #     patient_mock = self.util.create_patient_mock(user=self.user)
    #
    #     # Cria uma survey no Lime Survey
    #     sid = self.lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')
    #
    #     try:
    #
    #         # Cria um questionario
    #         questionnaire = QuestionnaireConfiguration.objects.create(lime_survey_id=sid, group=group,
    #                                                                   number_of_fills=1)
    #         questionnaire.save()
    #
    #         # Cria o TimeUnit para ser utilizado nos testes com intervalo de tempo
    #         time_unit = TimeUnit.objects.create(name='Horas')
    #         time_unit.save()
    #
    #         # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
    #         response = self.client.get(reverse('subjects', args=(group.pk,)))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(len(response.context['subject_list']), 0)
    #
    #         count_before_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         response = self.client.post(reverse('subject_insert', args=(group.pk, patient_mock.pk)))
    #         self.assertEqual(response.status_code, 302)
    #         count_after_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         self.assertEqual(count_after_insert_subject, count_before_insert_subject + 1)
    #
    #         # Reabre a tela de cadastro de participantes - devera conter ao menos um participante
    #         # cadastrado
    #         response = self.client.get(reverse('subjects', args=(group.pk,)))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(len(response.context['subject_list']), 1)
    #
    #         # Inserir participante ja inserido para o experimento
    #         count_before_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         response = self.client.post(reverse('subject_insert', args=(group.pk, patient_mock.pk)))
    #         self.assertEqual(response.status_code, 302)
    #         count_after_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         self.assertEqual(count_after_insert_subject, count_before_insert_subject)
    #
    #         subject = Subject.objects.all().first()
    #
    #         # Associar participante a Survey e iniciar preenchimento
    #         # Abrir a tela de associacao
    #         response = self.client.get(reverse('subject_questionnaire',
    #                                            args=[group.pk, subject.pk]))
    #         self.assertEqual(response.status_code, 200)
    #
    #         # Prepara para o a associacao entre preenchimento da Survey,
    #         # participante e experimento
    #         response = self.client.get(reverse('subject_questionnaire_response',
    #                                            args=[subject.pk, questionnaire.pk, ]))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['creating'], True)
    #
    #         # Dados para preenchimento da Survey
    #         self.data = {'date': ['29/08/2014'], 'action': ['save']}
    #
    #         # Inicia o preenchimento de uma Survey sem tabela de tokens iniciada
    #         response = self.client.post(reverse('subject_questionnaire_response',
    #                                             args=[subject.pk, questionnaire.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['FAIL'], False)
    #
    #         # Inicia o preenchimento de uma Survey INATIVA
    #         response = self.client.post(reverse('subject_questionnaire_response',
    #                                             args=[subject.pk, questionnaire.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['FAIL'], False)
    #
    #         status = self.lime_survey.activate_tokens(sid)
    #         self.assertEqual(status, 'OK')
    #
    #         # Ativar survey
    #         status = self.lime_survey.activate_survey(sid)
    #         self.assertEqual(status, 'OK')
    #
    #         # Inicia o preenchimento de uma Survey NORMAL
    #         response = self.client.post(reverse('subject_questionnaire_response',
    #                                             args=[subject.pk, questionnaire.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['FAIL'], True)
    #
    #         questionnaire_response = QuestionnaireResponse.objects.all().first()
    #
    #         # Acessa tela de atualizacao do preenchimento da Survey
    #         response = self.client.get(reverse('questionnaire_response_edit',
    #                                            args=[questionnaire_response.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['FAIL'], None)
    #
    #         # Atualiza o preenchimento da survey
    #         response = self.client.post(reverse('questionnaire_response_edit',
    #                                             args=[questionnaire_response.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertEqual(response.context['FAIL'], True)
    #
    #         response = self.client.get(reverse('questionnaire_response_edit',
    #                                            args=[questionnaire_response.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 200)
    #
    #         # Remove preenchimento da Survey
    #         count_before_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()
    #
    #         self.data['action'] = 'remove'
    #         response = self.client.post(reverse('questionnaire_response_edit',
    #                                             args=[questionnaire_response.pk, ]), self.data)
    #         self.assertEqual(response.status_code, 302)
    #
    #         count_after_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()
    #         self.assertEqual(count_before_delete_questionnaire_response - 1, count_after_delete_questionnaire_response)
    #
    #         # Remover participante associado a survey
    #         self.data = {'action': 'remove'}
    #         count_before_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         response = self.client.post(reverse('subject_questionnaire', args=(group.pk, subject.pk)),
    #                                     self.data)
    #         self.assertEqual(response.status_code, 302)
    #         count_after_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
    #         self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)
    #
    #     finally:
    #         # Deleta a survey gerada no Lime Survey
    #         status = self.lime_survey.delete_survey(sid)
    #         self.assertEqual(status, 'OK')

    def test_questionaire_view(self):
        """ Testa a visualizacao completa do questionario respondido no Lime Survey"""

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Teste-View",
                                               description="Descricao do Experimento-View")
        experiment.save()

        # Criar um grupo mock para ser utilizado no teste
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Descricao do Group-update")
        group.save()

        # Criar um Subject para o experimento
        patient_mock = self.util.create_patient_mock(user=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Cria um questionario
        questionnaire_configuration = QuestionnaireConfiguration(lime_survey_id=LIME_SURVEY_CODE_ID_TEST,
                                                                 group=group,
                                                                 number_of_fills=2)
        questionnaire_configuration.save()

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.questionnaire_configuration = questionnaire_configuration
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Visualiza preenchimento da Survey
        get_data = {'view': "experiment", 'status': "view"}

        response = self.client.get(reverse('questionnaire_response_view',
                                           args=[questionnaire_response.pk, ]), data=get_data)
        self.assertEqual(response.status_code, 200)

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.questionnaire_configuration = questionnaire_configuration
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_2
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Visualiza preenchimento da Survey
        response = self.client.get(reverse('questionnaire_response_view',
                                           args=[questionnaire_response.pk, ]), data=get_data)
        self.assertEqual(response.status_code, 200)

        # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
        response = self.client.get(reverse('subjects', args=(group.pk,)))
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

            group = Group.objects.create(experiment=experiment,
                                         title="Grupo-teste-updload",
                                         description="Descricao do Grupo-teste-updload")
            group.save()

        patient_mock = self.util.create_patient_mock(user=self.user)

        subject_mock = Subject.objects.all().first()

        if not subject_mock:
            subject_mock = Subject.objects.create(patient=patient_mock)
            subject_mock.patient = patient_mock
            subject_mock.save()

        self.assertEqual(get_object_or_404(Subject, pk=subject_mock.pk), subject_mock)

        subject_group = SubjectOfGroup.objects.all().first()
        if not subject_group:
            subject_group = SubjectOfGroup.objects.create(subject=subject_mock, group=group)

        subject_group.group = group
        subject_group.subject = subject_mock
        subject_group.save()

        # experiment.subjectofexperiment_set.add(subject_group)
        # experiment.save()

        self.assertEqual(get_object_or_404(Experiment, pk=experiment.pk), experiment)
        self.assertEqual(get_object_or_404(SubjectOfGroup, subject=subject_mock, group=group),
                         subject_group)

        # Upload Consent_form
        # Simula click no icone de acesso a pagina de upload do arquivo
        request = self.factory.get(reverse('upload_file', args=[subject_mock.pk, experiment.pk, ]))
        request.user = self.user
        response = upload_file(request, subject_id=subject_mock.pk, group_id=group.pk)

        self.assertEqual(response.status_code, 200)

        # Anexar arquivo
        consent_form_file = SimpleUploadedFile('quiz/consent_form.txt', 'rb')
        self.data = {'action': 'upload', 'consent_form': consent_form_file}
        url = reverse('upload_file', args=[group.pk, subject_mock.pk])
        # request = self.factory.post(url, self.data)d
        # request.user = self.user
        # response = upload_file(request, subject_id=subject_mock.pk, experiment_id=experiment.pk)
        response = self.client.post(reverse('upload_file', args=[group.pk, subject_mock.pk, ]), self.data,
                                    follow=True)
        # print response.content
        self.assertEqual(response.status_code, 200)

        # Remover arquivo
        self.data = {'action': 'remove'}
        response = self.client.post(reverse('upload_file', args=[group.pk, subject_mock.pk, ]), self.data)
        self.assertEqual(response.status_code, 302)


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