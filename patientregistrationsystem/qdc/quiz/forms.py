from django.forms import ModelForm
from models import Patient, PersonalData, SocialDemographicData, SocialHistoryData
from django.db import models

# Create the form class.


class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['cpf_id', 'name_txt', 'rg_id', 'medical_record_number']


class PersonalDataForm(ModelForm):
    class Meta:
        model = PersonalData
        fields = ['natural_of_txt', 'citizenship_txt', 'street_txt', 'zipcode_number', 'country_txt', 'state_txt',
                  'city_txt', 'phone_number', 'cellphone_number', 'email_txt', 'dt_birth_txt']


class SocialDemographicDataForm(ModelForm):
    #int sum_opt
    benefit_gov_bool = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))
    #tv_opt = models.IntegerField(choices=((0, 'TVoption0'), (1, 'TVoption1'), (2, 'TVoption2'), (3, 'TVoption3'), (4, 'TVoption4')))
    #dvd_opt = models.IntegerField(choices=)
    #radio_opt = models.IntegerField(choices=)
    #bath_opt = models.IntegerField(choices=)
    #automobile_opt = models.IntegerField(choices=)
    #wash_machine_opt = models.IntegerField(choices=)
    #refrigerator_opt = models.IntegerField(choices=)
    #freezer_opt = models.IntegerField(choices=)
    #house_maid_opt = models.IntegerField(choices=)
    #sum_opt = tv_opt +
    #social_class_opt = models.CharField(choices=(('A1', 42-46))))
    class Meta:
        model = SocialDemographicData
        fields = ['profession_txt', 'occupation_txt', 'benefit_gov_bool']


class SocialHistoryDataForm(ModelForm):
    smoker = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))
    ex_smoker = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))
    alcoholic = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))
    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'amount_cigarettes_opt', 'ex_smoker', 'alcoholic', 'alcohol_frequency', 'alcohol_period_opt', 'drugs_opt']