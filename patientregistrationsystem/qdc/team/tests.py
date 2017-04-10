# coding=utf-8

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.translation import ugettext as _

from .models import Person

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

        self.group1 = Group.objects.create(name='group1')
        self.group1.save()

        self.group2 = Group.objects.create(name='group2')
        self.group2.save()

    def test_person_list(self):
        """
        Test person list
        """

        # list of persons
        response = self.client.get(reverse("person_list"))
        self.assertEqual(response.status_code, 200)

        # should be empty
        self.assertEqual(len(response.context['persons']), 0)

    def test_person_create_access_register_screen(self):
        """Test the creation of a person - access register screen"""

        # access (get method) person create screen
        response = self.client.get(reverse('person_new'))
        self.assertEqual(response.status_code, 200)

    def test_person_create_wrong_option(self):
        """Test the creation of a person - using wrong option"""

        counter = User.objects.all().count()

        # POSTing "wrong" action
        self.data = {'action': 'wrong'}
        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(User.objects.all().count(), counter)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Action not available.'))
        self.assertEqual(response.status_code, 200)

    def test_person_create_posting_missing_information(self):
        """Test the creation of a person - posting missing information"""

        counter = User.objects.all().count()

        # POSTing missing information (person_form)
        self.data = {'action': 'save'}
        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(User.objects.all().count(), counter)
        self.assertGreaterEqual(len(response.context['person_form'].errors), 3)
        self.assertTrue('first_name' in response.context['person_form'].errors)
        self.assertTrue('last_name' in response.context['person_form'].errors)
        self.assertTrue('email' in response.context['person_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

        # POSTing missing information (user_form)
        self.data = {'action': 'save',
                     'optradio': '2',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br'}
        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(User.objects.all().count(), counter)
        self.assertGreaterEqual(len(response.context['user_form'].errors), 2)
        self.assertTrue('username' in response.context['user_form'].errors)
        self.assertTrue('password' in response.context['user_form'].errors)
        # self.assertTrue('groups' in response.context['user_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

    def test_person_create_with_login(self):
        """Test the creation of a person with login"""

        # person data
        self.data = {'action': 'save',
                     'optradio': '2',
                     'username': 'josesilva',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br',
                     'password': 'ze',
                     'groups': [self.group1.id]}

        count_before_insert = User.objects.all().count()

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(response.status_code, 302)

        counter = User.objects.all().count()
        self.assertEqual(counter, count_before_insert + 1)

        # list of persons. Should show one
        response = self.client.get(reverse("person_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['persons']), 1)

        # get added person
        person = Person.objects.filter(email=self.data['email'])[0]

        # person update screen
        response = self.client.get(reverse("person_edit", args=(person.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {'action': 'save',
                     'username': 'josesilva',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br',
                     'password': 'ze',
                     'groups': [self.group1.id]}
        response = self.client.post(reverse("person_edit", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(first_name=self.data['first_name']).exists())

        # update with changes
        self.data = {'action': 'save',
                     'username': 'josesilva',
                     'first_name': 'Joselito',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br',
                     'password': 'ze',
                     'groups': [self.group1.id, self.group2.id]}
        response = self.client.post(reverse("person_edit", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(first_name=self.data['first_name']).exists())

        # view person
        response = self.client.get(reverse('person_view', args=[person.id, ]))
        self.assertEqual(response.status_code, 200)

        # view person with "wrong" action
        self.data = {'action': 'wrong'}
        response = self.client.post(reverse("person_view", args=(person.id,)), self.data)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Action not available.'))
        self.assertEqual(response.status_code, 200)

        # remove person
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("person_view", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_person_create_with_invalid_email(self):
        """Test the creation of a person - invalid e-mail"""

        counter = User.objects.all().count()

        # person data
        self.data = {'action': 'save',
                     'optradio': '2',
                     'username': 'mariasilva',
                     'first_name': 'Maria',
                     'last_name': 'da Silva',
                     'email': 'mary',
                     'password': 'mary',
                     'groups': [self.group1.id]}

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(User.objects.all().count(), counter)
        self.assertGreaterEqual(len(response.context['person_form'].errors), 1)
        self.assertTrue('email' in response.context['person_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

    def test_person_create_with_existing_email(self):
        """Test the creation of a person - existing e-mail"""

        counter = User.objects.all().count()

        # person data
        self.data = {'action': 'save',
                     'optradio': '2',
                     'username': 'mariasilva',
                     'first_name': 'Maria',
                     'last_name': 'da Silva',
                     'email': 'test@dummy.com',
                     'password': 'mary',
                     'groups': [self.group1.id]}

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(User.objects.all().count(), counter)
        self.assertEqual(str(list(response.context['messages'])[0]), _('E-mail already exists.'))
        self.assertEqual(response.status_code, 200)

    def test_person_create_without_login(self):
        """Test the creation of a person with login"""

        # access (get method) person create screen
        response = self.client.get(reverse('person_new'))
        self.assertEqual(response.status_code, 200)

        # person data
        self.data = {'action': 'save',
                     'optradio': '1',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br'}

        count_before_insert = Person.objects.all().count()

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(response.status_code, 302)

        count_after_insert = Person.objects.all().count()
        self.assertEqual(count_after_insert, count_before_insert + 1)

        # get added person
        person = Person.objects.filter(email=self.data['email'])[0]

        # person update screen
        response = self.client.get(reverse("person_edit", args=(person.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {'action': 'save',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br'}
        response = self.client.post(reverse("person_edit", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(first_name=self.data['first_name']).exists())

        # update with changes
        self.data = {'action': 'save',
                     'first_name': 'Joselito',
                     'last_name': 'da Silva',
                     'email': 'teste@gmail.com.br'}
        response = self.client.post(reverse("person_edit", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(first_name=self.data['first_name']).exists())

        # view person
        response = self.client.get(reverse('person_view', args=[person.id, ]))
        self.assertEqual(response.status_code, 200)

        # remove person
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("person_view", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_person_create_deactivating(self):
        """Test the login deactivation for a person with login"""

        email = 'teste@gmail.com.br'

        # creating a person with login
        self.data = {'action': 'save',
                     'optradio': '2',
                     'username': 'josesilva',
                     'first_name': 'José',
                     'last_name': 'da Silva',
                     'email': email,
                     'password': 'ze',
                     'groups': [self.group1.id]}

        response = self.client.post(reverse('person_new'), self.data)
        self.assertEqual(response.status_code, 302)

        # get added person
        person = Person.objects.filter(email=self.data['email'])[0]

        # deactivating the login
        self.data = {'action': 'deactivate'}
        response = self.client.post(reverse("person_edit", args=(person.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Person.objects.filter(email=email).exists())
        self.assertTrue(User.objects.filter(email=email).exists())
        self.assertTrue(not User.objects.filter(email=email)[0].is_active)
