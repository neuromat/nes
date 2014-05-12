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
    #tv_opt = models.IntegerField(choices=((0, 'TVoption0'), (1, 'TVoption1'), (2, 'TVoption2'), (3, 'TVoption3'), (4, 'TVoption4')))
    #dvd_opt = models.IntegerField(choices=((0, 'DVDoption0'), (1, 'DVDoption1'), (2, 'DVDoption2'), (3, 'DVDoption3'), (4, 'DVDoption4')))
    #radio_opt = choices=((0, 'RADIOoption0'), (1, 'RADIOoption1'), (2, 'RADIOoption2'), (3, 'RADIOoption3'), (4, 'RADIOoption4'))
    #bath_opt = choices=((0, 'Bathsoption0'), (1, 'Bathsoption1'), (2, 'Bathsoption2'), (3, 'Bathsoption3'), (4, 'Bathsoption4'))
    #auto_opt = choices=((0, 'Autooption0'), (1, 'Autooption1'), (2, 'Autooption2'), (3, 'Autooption3'), (4, 'Autooption4'))
    #wm_opt = choices=((0, 'WMoption0'), (1, 'WMoption1'), (2, 'WMoption2'), (3, 'WMoption3'), (4, 'WMoption4'))
    #refrigerator_opt = choices=((0, 'Refrigoption0'), (1, 'Refrigoption1'), (2, 'Refrigoption2'), (3, 'Refrigoption3'), (4, 'Refrigoption4'))
    #freezer_opt = (0, 'Freezoption0'), (1, 'Freezoption1'), (2, 'Freezoption2'), (3, 'Freezoption3'), (4, 'Freezoption4'))
    #house_maid_opt = choices=((0, 'Employoption0'), (1, 'Employoption1'), (2, 'Employoption2'), (3, 'Employoption3'), (4, 'Employoption4'))
    #sum_opt = tv_opt +
    #social_class_opt = models.CharField(choices=(('A1', 42-46))))
    benefit_gov_bool = models.CharField(choices=(('False', 0), ('True', 1)))
    class Meta:
        model = SocialDemographicData
        fields = ['profession_txt', 'occupation_txt', 'tv_opt', 'dvd_opt', 'radio_opt', 'bath_opt', 'benefit_gov_bool',
                  'automobile_opt', 'wash_machine_opt', 'refrigerator_opt', 'freezer_opt', 'house_maid_opt']


class SocialHistoryDataForm(ModelForm):
    smoker = models.CharField(choices=(('True', 1), ('False', 0)))
    ex_smoker = models.CharField(choices=(('True', 1), ('False', 0)))
    alcoholic = models.CharField(choices=(('True', 1), ('False', 0)))
    #amount_cigarettes_opt = models.CharField(choices=(('1', 'cigOptions1'), ('2', 'cigOptions2'), ('3', 'cigOptions3')))
    #alcohol_frequency = models.CharField(choices=(('1', 'freqAlcohol1'), ('2', 'freqAlcohol2'), ('3', 'freqAlcohol3')))
    #alcohol_period_opt = models.CharField(choices=(('1', 'periodAlcohol1'), ('2', 'periodAlcohol2'), ('3', 'periodAlcohol3'), ('4', 'periodAlcohol4')))
    #drugs_opt = models.CharField(choices=(('1', 'drugsOption1'), ('2', 'drugsOption2'), ('3', 'drugsOption3')))
    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'amount_cigarettes_opt', 'ex_smoker', 'alcoholic', 'alcohol_frequency',
                  'alcohol_period_opt', 'drugs_opt']