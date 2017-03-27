# coding=utf-8

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from custom_user.views import User

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class ObjectsFactory(object):

    @staticmethod
    def system_authentication(instance):
        user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        factory = RequestFactory()
        logged = instance.client.login(username=USER_USERNAME, password=USER_PWD)
        return logged, user, factory


class PersonTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        self.group = Group.objects.create(name='group')
        self.group.save()


        # # Cria um estudo
        # self.research_project = ObjectsFactory.create_research_project()

    def test_person_list(self):
        """
        Test person list
        """

        # list of persons
        response = self.client.get(reverse("person_list"))
        self.assertEqual(response.status_code, 200)

        # should be empty
        self.assertEqual(len(response.context['persons']), 0)

    def test_person_create_basics(self):
        """Test the creation of a person """

        # access (get method) person create screen
        response = self.client.get(reverse('person_new'))
        self.assertEqual(response.status_code, 200)

        # person data
        self.data = {'action': 'save',
                     'optradio': '2',
                     'username': 'josesilva',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br',
                     'password': 'ze',
                     'groups': [self.group.id]}

        count_before_insert = User.objects.all().count()

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(response.status_code, 302)

        count_after_insert = User.objects.all().count()
        self.assertEqual(count_after_insert, count_before_insert + 1)
