# -*- coding: UTF-8 -*-
from importlib.util import resolve_name
import re

from django.http import HttpRequest
from sqlalchemy import false

from custom_user.models import Institution, User, UserProfile
from custom_user.tests_helper import create_user
from custom_user.views import (
    institution_create,
    institution_update,
    institution_view,
    user_update,
)
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.contrib.messages import get_messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.requests import RequestSite
from django.shortcuts import get_object_or_404
from django.template import loader
from django.test import SimpleTestCase, TestCase
from django.test.client import RequestFactory
from django.urls import resolve, reverse
from django.utils.http import int_to_base36
from django.utils.translation import gettext as _
from qdc import settings
from requests import Request


USER_USERNAME = "myadmin"
USER_PWD = "mypassword"
USER_NEW = "user_new"
USER_VIEW = "user_view"
USER_EDIT = "user_edit"
PATTERN = r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{6,20})"


class FormUserValidation(TestCase):
    user: User
    debug: bool

    def setUp(self):
        self.user = User.objects.create_superuser(
            username=USER_USERNAME,
            email="jenkins.neuromat@gmail.com",
            password=USER_PWD,
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.force_password_change = False
        profile.save()

        self.group: Group = Group.objects.create(name="group")
        self.group.save()

        self.debug = settings.DEBUG
        settings.DEBUG = False

        self.factory = RequestFactory()

        self.data = {
            "username": ["username"],
            "first_name": ["General"],
            "last_name": ["Test"],
            "password": ["Adm!123"],
            "password2": ["Adm!123"],
            "groups": [self.group.id],
            "email": ["email@test.com"],
            "action": "save",
        }

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def tearDown(self) -> None:
        settings.DEBUG = self.debug

    @staticmethod
    def reset(
        user_added: User | None = None,
        request: HttpRequest | None = None,
        domain_override: RequestSite | None = None,
        email_template_name: str = "registration/password_reset_email.html",
        use_https: bool = False,
        token_generator: PasswordResetTokenGenerator = default_token_generator,
    ) -> None:
        """Reset users password"""
        if not user_added.email:
            raise ValueError("Email address is required to send an email")

        if not domain_override:
            current_site: Site | RequestSite = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        loader.get_template(email_template_name)

        context = {
            "email": user_added.email,
            "domain": domain,
            "site_name": site_name,
            "uid": int_to_base36(user_added.id),
            "user": user_added,
            "token": token_generator.make_token(user_added),
            "protocol": use_https and "https" or "http",
        }

        subject_template_name = "registration/password_reset_subject.txt"
        subject = loader.render_to_string(subject_template_name, context)

        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())

        # CHANGES START HERE!
        plain_text_content = loader.render_to_string(
            email_template_name.replace("with_html", "plaintext"), context
        )
        html_content = loader.render_to_string(email_template_name, context)

        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives(
            subject,
            plain_text_content,
            "jenkins.neuromat@gmail.com",
            [user_added.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def test_user_invalid_username(self):
        self.data["username"] = ""
        self.data["login_enabled"] = True

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)

        self.assertFormError(response, "form", "username", "Este campo é obrigatório.")
        self.assertEqual(User.objects.filter(username="").count(), 0)

    def test_user_invalid_email(self):
        self.data["email"] = "email@invalid."
        self.data["login_enabled"] = True

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertFormError(
            response, "form", "email", "Informe um endereço de email válido."
        )
        self.assertEqual(User.objects.filter(username="").count(), 0)

    def test_user_email_already_registered(self):
        self.data["username"] = "email_registered"
        self.data["first_name"] = "Fulano"
        self.data["last_name"] = "de Tal"
        self.data["email"] = "jenkins.neuromat@gmail.com"
        self.data["login_enabled"] = False

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            _(
                "A researcher with this email address has already been registered before. "
                "Please contact your system administrator if you want to reactivate this account."
            ),
        )
        self.assertEqual(User.objects.filter(username="email_registered").count(), 0)

        self.assertEqual(response.status_code, 200)

    def test_researcher_without_user(self):
        del self.user
        self.data["login_enabled"] = False

        response = self.client.post(reverse(USER_NEW), self.data)
        self.assertEqual(response.status_code, 302)

    def test_user_passwords_doesnt_match(self):
        user_pwd = "test_pwd"
        self.data["username"] = user_pwd
        self.data["password"] = "abc123"
        self.data["password2"] = "acc123"
        self.data["login_enabled"] = True

        self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 1)

    def test_user_empty_password(self):
        user_pwd = "test_pwd_2"
        self.data["username"] = user_pwd
        self.data["password"] = ""
        self.data["login_enabled"] = True

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "password", "Este campo é obrigatório.")
        self.assertEqual(User.objects.filter(username=user_pwd).count(), 0)

    def test_user_create(self):
        username = "test_username"
        self.data["username"] = username
        self.data["login_enabled"] = True

        response = self.client.post(reverse(USER_NEW), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

    def test_user_create_failed_because_email_already_registered(self):
        email = "jenkins.neuromat@gmail.com"
        self.data = {
            "username": email,
            "email": email,
            "login_enabled": True,
            "action": "save",
        }

        response = self.client.post(reverse(USER_NEW), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)

    def test_user_create_mail_password_define(self):
        username = "test_username"
        self.data["email"] = "romulojosefranco@gmail.com"
        self.data["username"] = username
        self.data["login_enabled"] = True

        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        response = self.client.post(reverse(USER_NEW), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username=username).count(), 1)

        user_added = User.objects.filter(username=username).first()
        self.reset(user_added, request)

    def test_user_read(self):
        self.data["login_enabled"] = True
        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = user_update(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(USER_EDIT, args=[self.user.pk]), self.data)
        self.assertEqual(response.status_code, 302)

    def test_user_update_get(self):
        # Create an instance of a GET request.
        request = self.factory.get(reverse(USER_EDIT, args=[self.user.pk]))
        request.user = self.user

        # Test view() as if it were deployed at /quiz/patient/%id
        response = user_update(request, user_id=self.user.pk)
        self.assertEqual(response.status_code, 200)

    def test_user_update_post(self):
        first_name = "test_username"
        self.data["first_name"] = first_name
        self.data["login_enabled"] = True

        response = self.client.post(
            reverse(USER_EDIT, args=(self.user.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(id=self.user.pk).count(), 1)

        user_first_name = User.objects.filter(id=self.user.pk).first()

        self.assertEqual(user_first_name.first_name, first_name)

    def test_user_update_login_enable_false(self):
        email = "test@example.com"
        self.data = {
            "first_name": "Fulano",
            "last_name": "de Tal",
            "email": email,
            "login_enabled": False,
            "action": "save",
        }

        self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data)
        user_updated = User.objects.filter(first_name="Fulano")
        self.assertEqual(user_updated.count(), 1)

    def test_user_update_deactivate_user(self):
        self.data = {"action": "deactivate"}

        self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data)
        user = User.objects.first()
        self.assertTrue(user.is_active)
        self.assertFalse(user.has_usable_password())

    def test_user_update_with_password_flag_checked(self):
        email = "jenkins.neuromat@gmail.com"
        self.data = {
            "first_name": "Fulano",
            "last_name": "de Tal",
            "username": USER_USERNAME,
            "email": email,
            "login_enabled": True,
            "password_flag": True,
            "password": USER_PWD,
            "action": "save",
        }

        self.client.post(reverse(USER_EDIT, args=(self.user.pk,)), self.data)
        user_updated = User.objects.filter(first_name="Fulano")
        self.assertEqual(user_updated.count(), 1)

    def test_user_update_failed_because_email_already_registered(self):
        user_str = "user_to_update"
        new_user = User.objects.create_user(
            username=user_str, email="test@example.com", password="Bla!123"
        )
        new_user.is_staff = True
        new_user.is_active = True
        new_user.save()

        email = "jenkins.neuromat@gmail.com"
        self.data = {
            "first_name": "Fulano",
            "last_name": "de Tal",
            "username": user_str,
            "email": email,
            "login_enabled": False,
            "action": "save",
        }

        response = self.client.post(reverse(USER_EDIT, args=(new_user.pk,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)

    def test_user_remove(self):
        user_str = "user_remove"
        user_to_delete = User.objects.create_user(
            username=user_str, email="test@delete.com", password="Del!123"
        )
        user_to_delete.is_staff = True
        user_to_delete.is_superuser = True
        user_to_delete.is_active = True
        user_to_delete.save()
        self.assertEqual(User.objects.filter(username=user_str).count(), 1)

        self.data["action"] = "remove"

        response = self.client.post(
            reverse(USER_EDIT, args=(user_to_delete.pk,)), self.data, follow=True
        )

        self.assertEqual(response.status_code, 200)
        user_to_delete = get_object_or_404(User, pk=user_to_delete.pk)
        self.assertEqual(user_to_delete.is_active, False)

        # Create an instance of a GET request.
        request = self.factory.get(
            reverse(
                USER_EDIT,
                args=[
                    user_to_delete.pk,
                ],
            )
        )
        request.user = self.user

        response = user_update(request, user_id=user_to_delete.pk)
        self.assertEqual(response, None)

    def test_create_researcher_without_system_access(self):
        username = "fulano@detal.com"
        self.data["first_name"] = "Fulano"
        self.data["last_name"] = "de Tal"
        self.data["email"] = "fulano@detal.com"
        self.data["username"] = username
        self.data["login_enabled"] = False
        self.data["password"] = ""
        self.client.post(reverse(USER_NEW), self.data)

        fulano: User = User.objects.get(username=username)

        self.assertTrue(fulano.is_active)
        # https://stackoverflow.com/questions/71049149/django-unset-a-users-password-but-still-allow-password-reset
        self.assertTrue(fulano.has_usable_password())
        fulano.set_unusable_password()
        self.assertFalse(fulano.has_usable_password())

    def test_remove_researcher_without_system_access(self):
        username = "fulano@detal.com"
        self.data["first_name"] = "Fulano"
        self.data["last_name"] = "de Tal"
        self.data["email"] = "fulano@detal.com"
        self.data["username"] = username
        self.data["login_enabled"] = False
        self.client.post(reverse(USER_NEW), self.data)

        resercher = User.objects.get(username=username)
        self.data["action"] = "remove"
        response = self.client.post(
            reverse(USER_VIEW, args=(resercher.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)


class PasswordPattern(TestCase):
    """
    Test of the defined pattern

    (	    		#   Start
    (?=.*\d)		#   must contains one digit from 0-9
    (?=.*[a-z])		#   must contains one lowercase characters
    (?=.*[A-Z])		#   must contains one uppercase characters
    (?=.*[@#$%])	#   must contains one special symbols in the list "@#$%"
    .		        #   match anything with previous condition checking
    {6,20}	        #   length at least 6 characters and maximum of 20
    )               #   End
    """

    @staticmethod
    def confirm_password(pattern, password):
        return re.compile(pattern).match(password)

    def test_user_password_check_valid_pattern(self):
        password = "abcC2@!$"

        self.assertTrue(self.confirm_password(PATTERN, password), True)

    def test_user_password_check_invalid_pattern_only_letters(self):
        password = "abcdefgh"

        self.assertFalse(self.confirm_password(pattern=PATTERN, password=password))

    def test_user_password_check_invalid_pattern_only_numbers(self):
        password = "12345678"

        self.assertFalse(self.confirm_password(pattern=PATTERN, password=password))

    def test_user_password_check_invalid_pattern_without_special_symbols(self):
        password = "123abcDEF"

        self.assertFalse(self.confirm_password(pattern=PATTERN, password=password))

    def test_user_password_check_invalid_pattern_less_than_six_chars(self):
        password = "1aB!"

        self.assertFalse(self.confirm_password(pattern=PATTERN, password=password))


class InstitutionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME,
            email="jenkins.neuromat@gmail.com",
            password=USER_PWD,
        )
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.force_password_change = False
        profile.save()

        self.debug: bool = settings.DEBUG
        settings.DEBUG = False

        self.factory = RequestFactory()

        self.data = {
            "name": ["name"],
            "acronym": ["acronym"],
            "country": ["country"],
            "action": "save",
        }

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        Institution.objects.create(
            name="CEPID NeuroMat", acronym="NeuroMat", country="BR"
        )

    def tearDown(self) -> None:
        settings.DEBUG = self.debug

    def test_institution_new_status_code(self) -> None:
        url = reverse("institution_new")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "custom_user/institution_register.html")

    def test_institution_new_url_resolves_institution_new_view(self):
        view = resolve(r"/user/institution/new/")
        self.assertEqual(view.func, institution_create)

    def test_institution_create(self):
        self.data = {
            "name": "Faculdade de Medicina",
            "acronym": "FM",
            "country": "BR",
            "action": "save",
        }
        response = self.client.post(reverse("institution_new"), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Institution.objects.filter(name="Faculdade de Medicina").count(), 1
        )

    def test_institution_create_wrong_action(self) -> None:
        self.data = {
            "name": "Faculdade de Medicina",
            "acronym": "FM",
            "country": "BR",
            "action": "bla",
        }
        response = self.client.post(reverse("institution_new"), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)

    def test_institution_view_status_code(self) -> None:
        institution = Institution.objects.first()
        url = reverse("institution_view", args=(institution.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "custom_user/institution_register.html")

    def test_institution_view_url_resolves_institution_view_view(self):
        view = resolve("/user/institution/1/")
        self.assertEqual(view.func, institution_view)

    def test_institution_view_and_action_remove(self) -> None:
        institution = Institution.objects.first()
        self.data["action"] = "remove"
        self.client.post(reverse("institution_view", args=(institution.pk,)), self.data)
        self.assertEqual(Institution.objects.count(), 0)

    def test_institution_view_and_action_remove_denied_because_there_are_people_associated(
        self,
    ):
        institution = Institution.objects.first()
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.institution = institution
        profile.save()
        self.data["action"] = "remove"
        response = self.client.post(
            reverse("institution_view", args=(institution.pk,)), self.data
        )
        self.assertEqual(Institution.objects.count(), 1)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)

    def test_institution_view_and_action_remove_denied_because_there_is_institution_associated(
        self,
    ):
        parent = Institution.objects.create(
            name="Example", acronym="example", country="BR"
        )
        institution = Institution.objects.first()
        institution.parent = parent
        institution.save()
        self.data["action"] = "remove"
        response = self.client.post(
            reverse("institution_view", args=(parent.pk,)), self.data
        )
        self.assertEqual(Institution.objects.count(), 2)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)

    def test_institution_update_status_code(self):
        institution = Institution.objects.first()
        url = reverse("institution_edit", args=(institution.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "custom_user/institution_register.html")

    def test_institution_update_url_resolves_institution_update_view(self):
        view = resolve("/user/institution/edit/1/")
        self.assertEqual(view.func, institution_update)

    def test_institution_update(self) -> None:
        institution = Institution.objects.first()
        self.data = {
            "name": "RIDC NeuroMat",
            "acronym": "NeuroMat",
            "country": "BR",
            "action": "save",
        }
        response = self.client.post(
            reverse("institution_edit", args=(institution.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Institution.objects.filter(name="RIDC NeuroMat").count(), 1)


class PasswordResetTests(TestCase):
    def setUp(self) -> None:
        url = reverse("password_reset")
        self.response = self.client.get(url)
        self.debug: bool = settings.DEBUG
        settings.DEBUG = False

    def tearDown(self) -> None:
        settings.DEBUG = self.debug

    def test_status_code(self) -> None:
        self.assertEqual(self.response.status_code, 200)

    def test_csrf(self) -> None:
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_first_time_user_login_redirects_to_change_password_page(self) -> None:
        user, passwd = create_user(force_password_change=True)
        response = self.client.post(
            reverse("login"),
            data={"username": user.username, "password": passwd},
            follow=True,
        )
        # TODO: fetch_redirect_response=False check
        self.assertRedirects(response, reverse("password_change"))
