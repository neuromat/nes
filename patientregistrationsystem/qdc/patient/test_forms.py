from django.test import TestCase
from patient.models import *
from patient.forms import *
from django.core.files.uploadedfile import SimpleUploadedFile
from patient.views import *
from django.contrib.auth.models import User

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'

class PatientFormValidation(TestCase):
    def setUp(self):
        self.gender = Gender.objects.create(name='Masculino')
        self.gender.save()

        self.data = {
            'name': 'Patient for test',
            'gender': str(self.gender.id),
            'date_birth': '01/02/1995'
        }

    # Test if the form with only the required fields filled is valid
    def test_PatientForm_is_valid(self):
        patient = PatientForm(data={'name': self.data["name"], 'date_birth': self.data["date_birth"], 'gender': self.data["gender"]})
        self.assertTrue(patient.is_valid())

    # Test if the form with the option "anonymous patient?" marked is valid
    # When anonymous patient is marked, the field "name" is not required anymore
    def test_PatientForm_is_valid_with_anonymous_patient(self):
        patient = PatientForm(data={'anonymous': True,'date_birth': self.data["date_birth"], 'gender': self.data["gender"]})
        self.assertTrue(patient.is_valid())

    # Test if the form without the required fields filled is not valid
    def test_PatientForm_is_not_valid(self):
        patient = PatientForm(data={'name': "", 'date_birth': "", 'gender': ""})
        self.assertFalse(patient.is_valid())

    # Test if the form without the "name" of the patient filled is not valid
    def test_PatientForm_is_not_valid_without_name(self):
        patient = PatientForm(data={'name': "", 'date_birth': self.data["date_birth"], 'gender': self.data["gender"]})
        self.assertFalse(patient.is_valid())
        self.assertEqual(patient.errors["name"], ["Nome deve ser preenchido"])

    # Test if the form without the "date of birth" of the patient filled is not valid
    def test_PatientForm_is_not_valid_without_date_birth(self):
        patient = PatientForm(data={'name': self.data["name"], 'date_birth': "", 'gender': self.data["gender"]})
        self.assertFalse(patient.is_valid())
        self.assertEqual(patient.errors["date_birth"], ["Este campo é obrigatório."])

    # Test if the form without the "gender" of the patient filled is not valid
    def test_PatientForm_is_not_valid_without_gender(self):
        patient = PatientForm(data={'name': self.data["name"], 'date_birth': self.data["date_birth"], 'gender': ""})
        self.assertFalse(patient.is_valid())
        self.assertEqual(patient.errors["gender"], ["Este campo é obrigatório."])

class TelephoneFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        type = Telephone.objects.create(type='HO',changed_by_id=self.user.id,patient_id=1)
        self.data = {
            'number': '123456789',
            'type': type.type,
            'note': '01/02/1995'
        }

    # Test if the form with the fields filled is valid
    def test_TelephoneForm_is_valid(self):
        telephone = TelephoneForm(data={'number':self.data["number"],'type':self.data["type"],'note':self.data["note"]})
        self.assertTrue(telephone.is_valid())

    # Test if the form without any of the fields filled is not valid
    def test_TelephoneForm_is_not_valid(self):
        telephone = TelephoneForm(data={'number':"",'type':"",'note':""})
        self.assertFalse(telephone.is_valid())

    # Test if the form without the "number" of the patient filled is not valid
    def test_TelephoneForm_is_not_valid_without_number(self):
        telephone = TelephoneForm(data={'number':"",'type':self.data["type"],'note':self.data["note"]})
        self.assertFalse(telephone.is_valid())

    # Test if the form without the "type" of the patient filled is not valid
    def test_TelephoneForm_is_not_valid_without_type(self):
        telephone = TelephoneForm(data={'number':self.data["number"],'type':"",'note':self.data["note"]})
        self.assertTrue(telephone.is_valid())

    # Test if the form without the "note" of the patient filled is not valid
    def test_TelephoneForm_is_not_valid_without_note(self):
        telephone = TelephoneForm(data={'number': self.data["number"], 'type': self.data["type"], 'note': ""})
        self.assertTrue(telephone.is_valid())

class SocialDemographicDataFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        payment = Payment.objects.create(name='SUS')
        payment.save()
        fleshtone = FleshTone(name='Branco')
        fleshtone.save()
        religion = Religion(name='Budismo')
        religion.save()
        schooling = Schooling(name='Superior Completo')
        schooling.save()

        self.data = {
            'natural_of':'São Paulo',
            'citizenship':'Brasil',
            'profession':'Estudante',
            'occupation':'Study',
            'religion': religion.id,
            'payment': payment.id,
            'flesh_tone': fleshtone.id,
            'schooling': schooling.id,
            'patient_schooling': schooling.id,
            'tv':'1',
            'dvd':'1',
            'radio':'1',
            'bath':'1',
            'automobile':'1',
            'wash_machine':'1',
            'refrigerator':'1',
            'freezer':'1',
            'house_maid':'1',
            'benefit_government': True
        }

    # Test if the form with the fields filled is valid
    def test_SocialDemographicData_is_valid(self):
        socialdemodata = SocialDemographicDataForm(data=self.data)
        self.assertTrue(socialdemodata.is_valid())

    # Test if the social class field is empty, once it's only calculated after saving the form
    def test_Social_Class_is_empty(self):
        # First we have to confirm that the form is valid
        socialdemodata = SocialDemographicDataForm(data=self.data)
        self.assertTrue(socialdemodata.is_valid())

        self.assertEqual(socialdemodata.cleaned_data['social_class'],'')

    # Test if the form is invalid if one field is passed with a different format defined by the form to it
    def test_SocialDemographicData_is_not_valid(self):
        self.data['schooling']='NotSelect'
        socialdemodata = SocialDemographicDataForm(data=self.data)
        self.assertFalse(socialdemodata.is_valid())

class SocialHistoryFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        amount_cigarettes = AmountCigarettes.objects.create(name='More than 3 packs')
        amount_cigarettes.save()
        alcohol_frequency = AlcoholFrequency.objects.create(name='Sporadically')
        alcohol_frequency.save()
        alcohol_period = AlcoholPeriod.objects.create(name='Less than 1 year')
        alcohol_period.save()

        self.data = {
            'smoker': True,
            'amount_cigarettes': amount_cigarettes.id,
            'ex_smoker': False,
            'alcoholic': True,
            'alcohol_frequency': alcohol_frequency.id,
            'alcohol_period': alcohol_period.id,
            'drugs': 'ja_fez'
        }

    # Test if the form with the fields filled is valid
    def test_SocialHistory_is_valid(self):
        socialhistory = SocialHistoryDataForm(data=self.data)
        self.assertTrue(socialhistory.is_valid())

    # Test if the form of a smoker patient is valid
    def test_SocialHistory_is_valid_with_smoker_patient(self):
        socialhistory = SocialHistoryDataForm(data=self.data)
        self.assertTrue(socialhistory.is_valid())

    # Test if the form of a non-smoker patient is valid and the dependent field doesn't have any value
    def test_SocialHistory_is_valid_with_non_smoker_patient(self):
        self.data["smoker"]=False
        socialhistory = SocialHistoryDataForm(data=self.data)
        self.assertTrue(socialhistory.is_valid())

    # Test if the form of a non-alcoholic patient is valid and the dependent fields don't have any value
    def test_SocialHistory_is_valid_with_non_alcoholic_patient(self):
        self.data["alcoholic"]=False
        socialhistory = SocialHistoryDataForm(data=self.data)
        self.assertTrue(socialhistory.is_valid())

    # Test if the form of a alcoholic patient is valid
    def test_SocialHistory_is_valid_with_alcoholic_patient(self):
        socialhistory = SocialHistoryDataForm(data=self.data)
        self.assertTrue(socialhistory.is_valid())

    # Test if the form empty is not valid
    def test_SocialHistory_is_not_valid(self):
        socialhistory = SocialHistoryDataForm()
        self.assertFalse(socialhistory.is_valid())

class MedicalRecordFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.data = {
            'description': 'Description',
            'date': '01/02/1995'
        }

    def test_Medical_Record_is_valid(self):
        medicalrecord = ComplementaryExamForm(data=self.data)
        self.assertTrue(medicalrecord.is_valid())

    def test_Medical_Record_is_not_valid(self):
        medicalrecord = ComplementaryExamForm(data={'description': "",'date': ""})
        self.assertFalse(medicalrecord.is_valid())

    def test_Medical_Record_is_not_valid_without_description(self):
        medicalrecord = ComplementaryExamForm(data={'description': "",'date': self.data['date']})
        self.assertFalse(medicalrecord.is_valid())

    def test_Medical_Record_is_not_valid_without_date(self):
        medicalrecord = ComplementaryExamForm(data={'description': self.data['description'],'date': ""})
        self.assertFalse(medicalrecord.is_valid())

class QuestionnaireResponseFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.data = {
            'date': '01/02/1995'
        }

    def test_Questionnaires_Response_is_valid(self):
        questionnaireresponse = QuestionnaireResponseForm(data=self.data)
        self.assertTrue(questionnaireresponse.is_valid())

    def test_Questionnaires_Response_is_not_valid_without_date(self):
        self.data['date']= ''
        questionnaireresponse = QuestionnaireResponseForm(data=self.data)
        self.assertFalse(questionnaireresponse.is_valid())

    def test_Questionnaires_Response_is_not_valid_with_future_date(self):
        self.data['date']= '01/02/2019'
        questionnaireresponse = QuestionnaireResponseForm(data=self.data)
        self.assertFalse(questionnaireresponse.is_valid())