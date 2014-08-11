# -*- coding: UTF-8 -*-
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import Group

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site, get_current_site
from django.core.mail import send_mail
from django.template import loader
from django.template.context import Context
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _
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

        self.user = User.objects.create_user(username=USER_USERNAME, email='jenkins.neuromat@gmail.com', password=USER_PWD)
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

    def reset(self, user_added=None, request=None, domain_override=None, email_template_name='registration/password_reset_email.html',
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
        #send_mail(_("Your account for %s") % site_name, t.render(Context(c)), None, [user_added.email])
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

        self.client.post(reverse(USER_NEW), self.data, follow=True)
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
