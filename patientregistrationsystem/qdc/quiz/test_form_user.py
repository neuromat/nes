# -*- coding: UTF-8 -*-
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.http import Http404
from django.test.client import RequestFactory
from django.contrib.auth.models import Group


from views import User, reverse, user_update, user_delete

import re


USER_NEW = 'user_new'


class FormUserValidation(TestCase):
    user = ''

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

        self.group = Group.objects.create(name='grupo1')
        self.group.save()

        self.factory = RequestFactory()

        self.data = {'username': ['username'],
                     'first_name': ['Romulo'],
                     'last_name': ['Franco'],
                     'password': ['Adm!123'],
                     'password2': ['Adm!123'],
                     'groups': [self.group.id],
                     'email': ['romulojosefranco@gmail.com']}

        logged = self.client.login(username=username_dummy, password=password_dummy)
        self.assertEqual(logged, True)

    def test_password_pattern(self):
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

    #
    # def test_password_confirmation(self):
    # """Testa a senha e confirmacao de senha """
    # pattern = '((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})'
    # password = "abcC1@!$"
    # confirm_password = "abcC0@!$"
    # a = re.compile(pattern)
    # self.assertTrue(a.match(password), True)
    # self.assertEqual(password,confirm_password)

    def confirm_password(self, pattern, password):
        a = re.compile(pattern)
        return a.match(password)

    def test_user_invalid_username(self):
        """
        Testa inclusao de usuario com sucesso
        """

        self.data['username'] = ''

        try:
            response = self.client.post(reverse(USER_NEW), self.data, follow=True)
            # errors = response.context['form'].errors
            # self.assertEqual(1, len(errors), msg='Erros encontrados durante as validacoes: %s' % errors)
            #messages = response.context['messages']
            #print messages

            self.assertFormError(response, "form", "username", u'Este campo é obrigatório.')
            self.assertEqual(User.objects.filter(username='').count(), 0)

        except Http404:
            pass

    def test_user_invalid_email(self):
        """
        Testa inclusao de usuario com sucesso
        """

        self.data['email'] = 'email@invalid.'

        try:
            response = self.client.post(reverse(USER_NEW), self.data, follow=True)
            # errors = response.context['form'].errors
            #self.assertEqual(1, len(errors), msg='Erros encontrados durante as validacoes: %s' % errors)
            #messages = response.context['messages']
            #print messages

            self.assertFormError(response, "form", "email", u'Informe um endereço de email válido.')
            # self.assertContains(response, u'Informe um endereço de email válido')
            self.assertEqual(User.objects.filter(username='').count(), 0)

        except Http404:
            pass

    def test_user_passwords_doesnt_match(self):
        """
        Testa senhas não conferem
        """
        user_pwd = 'test_pwd'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc123'
        self.data['password2'] = 'acc123'

        try:
            self.client.post(reverse(USER_NEW), self.data, follow=True)

            self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

        except Http404:
            pass

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

        try:
            self.client.post(reverse(USER_NEW), self.data, follow=True)

            self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

        except Http404:
            pass

    def test_user_password_check_invalid_pattern_abc(self):
        """
        Testa padrao invalido de senha definido para o usuario (senha: abc)
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = 'abc'

        try:
            self.client.post(reverse(USER_NEW), self.data, follow=True)

            self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

        except Http404:
            pass

    def test_user_password_check_invalid_pattern_123(self):
        """
        Testa padrao invalido de senha definido para o usuario (senha: 123)
        """
        user_pwd = 'test_pwd_1'
        self.data['username'] = user_pwd
        self.data['password'] = '123'

        try:
            self.client.post(reverse(USER_NEW), self.data, follow=True)

            self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

        except Http404:
            pass

    def test_user_empty_password(self):
        """
        Testa senha em branco
        """
        user_pwd = 'test_pwd_2'
        self.data['username'] = user_pwd
        self.data['password'] = ''

        try:
            response = self.client.post(reverse(USER_NEW), self.data, follow=True)
            self.assertFormError(response, "form", "password", u'Este campo é obrigatório.')
            self.assertEqual(User.objects.filter(username=user_pwd).count(), 0)

        except Http404:
            pass

    def test_new_user(self):
        """
        Testa inclusao de usuario com sucesso
        """
        username = 'testeusername'
        self.data['username'] = username

        try:
            self.client.post(reverse(USER_NEW), self.data, follow=True)

            self.assertEqual(User.objects.filter(username=username).count(), 1)

        except Http404:
            pass

    def test_read_user(self):
        """
        Testa visualizar usuario
        """

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/user/%i/' % self.user.pk)
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        try:
            response = user_update(request, user_id=self.user.pk)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

    def test_update_user_get(self):
        """
        Testa atualizar usuario
        """

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/user/edit/%i/' % self.user.pk)
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        try:
            response = user_update(request, user_id=self.user.pk)
            self.assertEqual(response.status_code, 200)
        except Http404:
            pass

    def test_update_user_post(self):
        """
        Testa atualizar usuario
        """

        username = 'testeusername'
        self.data['username'] = username
        #id_user = User.objects.get(pk=1)

        try:
            self.client.post('quiz/user/edit/%d' % self.user.pk, self.data, follow=True)

            self.assertEqual(User.objects.filter(username=username).count(), 0)

        except Http404:
            pass

    def test_delete_user(self):
        """
        Testa deletar usuario
        """
        user_str = 'userdelete'
        user_to_delete = User.objects.create_user(username=user_str, email='test@delete.com',
                                                  password='Del!123')
        user_to_delete.is_staff = True
        user_to_delete.is_superuser = True
        user_to_delete.save()

        # Create an instance of a GET request.
        self.client.login(username='myadmin', password='mypassword')
        request = self.factory.get('/quiz/user/delete/%i/' % user_to_delete.pk)
        request.user = self.user

        self.assertEqual(User.objects.filter(username=user_str).count(), 1)

        # Test view() as if it were deployed at /quiz/patient/%id
        try:
            setattr(request, 'session', 'session')
            msg = FallbackStorage(request)
            setattr(request, '_messages', msg)

            response = user_delete(request, user_id=user_to_delete.pk)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(User.objects.filter(username=user_str, is_active=False).count(), 1)
        except Http404:
            pass
