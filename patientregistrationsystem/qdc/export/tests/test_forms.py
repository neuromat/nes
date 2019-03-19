# coding=utf-8
from django.test import TestCase
from export.forms import *
from patient.models import Gender, MaritalStatus
from django.contrib.auth.models import User

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class ParticipantsSelectionFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.gender = Gender.objects.create(name="Masculino")

    def test_ParticipantsSelectionForm_is_valid(self):

        self.data = {
            'gender': self.gender.id,
            'country': 'BR',
            'state': 'Bahia',
            'city': 'Porto Seguro'
        }

        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_ParticipantsSelectionForm_is_valid_with_only_gender(self):
        gender = Gender.objects.create(name="Masculino")
        self.data = {'gender': gender.id}
        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_ParticipantsSelectionForm_is_valid_with_only_marital_status(self):
        maritalstatus = MaritalStatus.objects.create(name="Solteiro")
        self.data = {'maritalstatus': maritalstatus.id}
        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_ParticipantsSelectionForm_is_valid_with_only_country(self):
        self.data = {'country': 'BR'}
        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_ParticipantsSelectionForm_is_valid_with_only_state(self):
        self.data = {'state': 'Bahia'}
        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_ParticipantsSelectionForm_is_valid_with_only_city(self):
        self.data = {'city': 'Porto Seguro'}
        export = ParticipantsSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())


class AgeIntervalFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {
            'min_age': 1,
            'max_age': 100
        }

    def test_AgeIntervalForm_is_valid(self):
        export = AgeIntervalForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_AgeIntervalForm_is_not_valid(self):
        del self.data['min_age']
        del self.data['max_age']
        export = AgeIntervalForm(data=self.data)
        self.assertFalse(export.is_valid())

    def test_AgeIntervalForm_is_not_valid_without_min_age(self):
        del self.data['min_age']
        export = AgeIntervalForm(data=self.data)
        self.assertFalse(export.is_valid())

    def test_AgeIntervalForm_is_not_valid_without_max_age(self):
        del self.data['max_age']
        export = AgeIntervalForm(data=self.data)
        self.assertFalse(export.is_valid())

    def test_AgeIntervalForm_is_not_valid_with_min_age_higher_than_max_age(self):
        self.data['max_age'] = 1
        self.data['min_age'] = 2
        export = AgeIntervalForm(data=self.data)
        self.assertFalse(export.is_valid())


class DiagnosisSelectionFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {'description': 'CID'}

    def test_DiagnosisSelectionForm_is_valid(self):
        export = DiagnosisSelectionForm(data=self.data)
        self.assertTrue(export.is_valid())

    def test_DiagnosisSelectionForm_is_not_valid(self):
        self.data['description'] = ""
        export = DiagnosisSelectionForm(data=self.data)
        self.assertFalse(export.is_valid())
