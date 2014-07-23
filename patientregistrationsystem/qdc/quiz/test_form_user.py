# -*- coding: UTF-8 -*-
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import Group

from views import User, reverse, user_update, user_delete

import re

USER_EDIT = 'user_edit'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
USER_NEW = 'user_new'


class FormUserValidation(TestCase):
    user = ''

    def setUp(self):
        """ Configura autenticacao e variaveis para iniciar cada teste """
        print 'Set up for', self._testMethodName

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.group = Group.objects.create(name='group')
        self.group.save()

        self.factory = RequestFactory()

        self.data = {'username': ['username'],
                     'first_name': ['General'],
                     'last_name': ['Test'],
                     'password': ['Adm!123'],
                     'password2': ['Adm!123'],
                     'groups': [self.group.id],
                     'email': ['email@test.com']}

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

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

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

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
        user_to_delete.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse('user_delete', args=(user_to_delete.pk,)))
        request.user = self.user

        self.assertEqual(User.objects.filter(username=user_str).count(), 1)

        # Test view() as if it were deployed at /quiz/patient/%id

        setattr(request, 'session', 'session')
        msg = FallbackStorage(request)
        setattr(request, '_messages', msg)

        response = user_delete(request, user_id=user_to_delete.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username=user_str, is_active=False).count(), 1)
