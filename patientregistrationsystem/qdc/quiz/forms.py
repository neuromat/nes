from django.forms import ModelForm
from models import Patient, PersonalData
from django.db import models

# Create the form class.
class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = ['cpf_id', 'name_txt']

class PersonalDataForm(ModelForm):
    benefit_gov_bool = models.BooleanField(choices=((True, 'Yes'), (False, 'No')))
    class Meta:
        model = PersonalData
        fields = ['dt_birth_txt', 'benefit_gov_bool', 'profession_txt', 'occupation_txt', 'years_studying_int']
