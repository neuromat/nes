# coding=utf-8
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from experiment.models import Experiment, QuestionnaireConfiguration
from experiment.views import experiment_update

from quiz.views import User, GenderOption

EXPERIMENT_LIST = 'experiment_list'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class ExperimentTest(TestCase):
    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        self.gender_opt.save()

        # self.data = {'name_txt': 'Patient for test',
        # 'cpf_id': '374.276.738-08',
        # 'gender_opt': str(self.gender_opt.id),
        # 'date_birth_txt': '01/02/1995',
        # 'email_txt': 'email@email.com'}

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
    def setUp(self):
        """
        Configura autenticacao e variaveis para iniciar cada teste

        """
        print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        self.gender_opt = GenderOption.objects.create(gender_txt='Masculino')
        self.gender_opt.save()

    def test_questionnaire_create(self):
        """Testa a criacao de um questionario para um dado experimento"""

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()

        # Abre tela de cadastro de questionario
        response = self.client.get(reverse('questionnaire_new', args=(experiment.pk,)))
        self.assertEqual(response.status_code, 200)

        count_before_insert = QuestionnaireConfiguration.objects.all().count()

        # Cria um questionario com os dados default apresentados em tela
        count_before_insert = QuestionnaireConfiguration.objects.all().count()
        self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': ['426494']}
        response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        count_after_insert = QuestionnaireConfiguration.objects.all().count()
        self.assertEqual(count_after_insert, count_before_insert + 1)

        # Criar um questionario com dados incompletos - Codigo Questionario invalido
        count_before_insert = QuestionnaireConfiguration.objects.all().count()
        self.data = {'action': ['save'], 'number_of_fills': ['1'], 'questionnaire_selected': [0]}
        response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        count_after_insert = QuestionnaireConfiguration.objects.all().count()
        self.assertEqual(count_after_insert,
                         count_before_insert + 1)  # TODO Verificar este teste, esta permitindo codigo de questionario do Lime Survey Invalido

        # Criar um questionario com intervalo de preenchimento
        count_before_insert = QuestionnaireConfiguration.objects.all().count()
        self.data = {'interval_between_fills_value': ['12'],
                     'number_of_fills': ['3'],
                     'questionnaire_selected': ['642916'],
                     'interval_between_fills_unit': ['1'],
                     'action': ['save']}

        response = self.client.post(reverse('questionnaire_new', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        count_after_insert = QuestionnaireConfiguration.objects.all().count()
        self.assertEqual(count_after_insert, count_before_insert)

    def test_questionnaire_update(self):
        """ Teste atualizacao de um questionario """






