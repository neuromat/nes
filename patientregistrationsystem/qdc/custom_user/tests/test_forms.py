# -*- coding: UTF-8 -*-
from custom_user.views import *
from django.contrib.auth.models import Group, User
from django.test import TestCase
from custom_user.forms import InstitutionForm, UserForm, ResearcherForm

USER_USERNAME = "myadmin"
USER_PWD = "mypassword"


# Tests of the form of institutions
class InstitutionFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.data = {"name": "Institution", "acronym": "for Test", "country": "BR"}

    # Test if the form with only the required fields filled is valid
    def test_InstitutionForm_is_valid(self):
        institution = InstitutionForm(
            data={
                "name": self.data["name"],
                "acronym": self.data["acronym"],
                "country": self.data["country"],
            }
        )
        self.assertTrue(institution.is_valid())

    # Test if the form without the name is not valid
    def test_InstitutionForm_is_not_valid_without_name(self):
        institution = InstitutionForm(
            data={
                "name": "",
                "acronym": self.data["acronym"],
                "country": self.data["country"],
            }
        )
        self.assertFalse(institution.is_valid())

    # Test if the form without the acronym is not valid
    def test_InstitutionForm_is_not_valid_without_acronym(self):
        institution = InstitutionForm(
            data={
                "name": self.data["name"],
                "acronym": "",
                "country": self.data["country"],
            }
        )
        self.assertFalse(institution.is_valid())

    # Test if the form without the country is not valid
    def test_InstitutionForm_is_not_valid_without_country(self):
        institution = InstitutionForm(
            data={
                "name": self.data["name"],
                "acronym": self.data["acronym"],
                "country": "",
            }
        )
        self.assertFalse(institution.is_valid())


# Tests of the form of users with login and password
class UserFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.group = Group.objects.create(name="Senior researcher")
        self.group.save()

        self.data = {
            "first_name": "First",
            "last_name": "Last 2018",
            "email": "teste2018@hotmail.com",
            "username": "Username2018",
            "password": "Password",
            "groups": [self.group.id],
        }

    # Test if the form with all the required fields filled is valid
    def test_UserForm_is_valid(self):
        userbeingcreated = UserForm(data=self.data)
        self.assertTrue(userbeingcreated.is_valid())

    # Test if the form without the first name is not valid
    def test_UserForm_is_not_valid_without_first_name(self):
        self.data["first_name"] = ""
        userbeingcreated = UserForm(data=self.data)
        self.assertFalse(userbeingcreated.is_valid())

    # Test if the form with an already registered email is not valid
    def test_UserForm_is_not_valid_with_duplicated_email(self):
        user_being_created = UserForm(data=self.data)
        user_being_created.save()

        self.data["first_name"] = "Second"
        self.data["username"] = "Username22018"
        new_user_being_created = UserForm(data=self.data)
        self.assertFalse(new_user_being_created.is_valid())

    # Test if the form without the last name is not valid
    def test_UserForm_is_not_valid_without_last_name(self):
        self.data["last_name"] = ""
        userbeingcreated = UserForm(data=self.data)
        self.assertFalse(userbeingcreated.is_valid())

    # Test if the form without the email is not valid
    def test_UserForm_is_not_valid_without_email(self):
        self.data["email"] = ""
        userbeingcreated = UserForm(data=self.data)
        self.assertFalse(userbeingcreated.is_valid())

    # Test if the form without the username is not valid
    def test_UserForm_is_not_valid_without_username(self):
        self.data["username"] = ""
        userbeingcreated = UserForm(data=self.data)
        self.assertFalse(userbeingcreated.is_valid())

    # Test if the form without the password is not valid
    def test_UserForm_is_not_valid_without_password(self):
        self.data["password"] = ""
        userbeingcreated = UserForm(data=self.data)
        self.assertFalse(userbeingcreated.is_valid())

    # Test if the form without the group is not valid
    # def test_UserForm_is_not_valid_without_group(self):
    #    self.data['groups']=""
    #    userbeingcreated = UserForm(data=self.data)
    #    self.assertFalse(userbeingcreated.is_valid())


# Tests of the form of researchers (users without login and password)
class ResearcherFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.data = {
            "first_name": "First",
            "last_name": "Last 2018",
            "email": "teste2018@hotmail.com",
        }

    # Test if the form with all the required fields filled is valid
    def test_ResearcherForm_is_valid(self):
        researcher = ResearcherForm(data=self.data)
        self.assertTrue(researcher.is_valid())

    # Test if the form without the first name is not valid
    def test_ResearcherForm_is_not_valid_without_first_name(self):
        self.data["first_name"] = ""
        researcher = ResearcherForm(data=self.data)
        self.assertFalse(researcher.is_valid())

    # Test if the form without the last name is not valid
    def test_ResearcherForm_is_not_valid_without_last_name(self):
        self.data["last_name"] = ""
        researcher = ResearcherForm(data=self.data)
        self.assertFalse(researcher.is_valid())

    # Test if the form without the email is not valid
    def test_ResearcherForm_is_not_valid_without_email(self):
        self.data["email"] = ""
        researcher = ResearcherForm(data=self.data)
        self.assertFalse(researcher.is_valid())
