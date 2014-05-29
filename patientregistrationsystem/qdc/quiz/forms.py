# coding=utf-8
from django.forms import ModelForm, TextInput, DateInput
from models import Patient, SocialDemographicData, SocialHistoryData
from django.db import models
from quiz_widget import SelectBoxCountries, SelectBoxState


# Create the form class.
class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = [
            'cpf_id', 'name_txt', 'rg_id', 'medical_record_number', 'natural_of_txt', 'citizenship_txt', 'street_txt',
            'zipcode_number', 'country_txt', 'state_txt', 'city_txt', 'phone_number', 'cellphone_number', 'email_txt',
            'dt_birth_txt'
        ]
        widgets = {
            'name_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome completo',
                                         'id': "full_name", 'autofocus': "true"}),
            'cpf_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CPF',
                                       'id': "cpf_id"}),
            'rg_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar RG',
                                      'id': "rg_id"}),
            'natural_of_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar Naturalidade',
                                               'id': "naturalOf"}),
            'street_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua - Complemento',
                                           'id': "street_txt"}),
            'zipcode_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CEP',
                                         'id': "zipcode"}),
            'city_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar cidade',
                                         'id': "city"}),
            'phone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar telefone para contato',
                                         'id': "phone"}),
            'cellphone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar celular',
                                         'id': "cellphone"}),
            'email_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar e-mail',
                                         'id': "email"}),
            'medical_record_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar número do prontuário',
                                         'id': "records_number"}),
            'citizenship_txt': SelectBoxCountries(attrs={'id': 'id_chosen_country', 'data-flags': 'true'}),
            'country_txt': SelectBoxCountries(attrs={'id': 'id_country_state_address', 'data-flags': 'true'}),
            'state_txt': SelectBoxState(attrs={'data-country': 'id_country_state_address', 'id': 'id_chosen_state'})
        }
        error_messages = {
            'name_txt': {
                'required': 'Nome não preenchido'
            }
        }

    ## Este código traz os campos em modo readonly ao retornar a busca.
    ##
    # If in search mode set widget attribute 'readonly'
    # def __init__(self, *args, **kwargs):
    #     super(PatientForm, self).__init__(*args, **kwargs)
    #     instance = getattr(self, 'instance', None)
    #     if instance and instance.pk:
    #         self.fields['name_txt'].widget.attrs['readonly'] = True
    #         self.fields['cpf_id'].widget.attrs['readonly'] = True
    #         self.fields['rg_id'].widget.attrs['readonly'] = True
    #         self.fields['natural_of_txt'].widget.attrs['readonly'] = True
    #         self.fields['street_txt'].widget.attrs['readonly'] = True
    #         self.fields['zipcode_number'].widget.attrs['readonly'] = True
    #         self.fields['city_txt'].widget.attrs['readonly'] = True
    #         self.fields['phone_number'].widget.attrs['readonly'] = True
    #         self.fields['cellphone_number'].widget.attrs['readonly'] = True
    #         self.fields['email_txt'].widget.attrs['readonly'] = True
    #         self.fields['medical_record_number'].widget.attrs['readonly'] = True
    #         self.fields['dt_birth_txt'].widget.attrs['readonly'] = True
    ##


class SocialDemographicDataForm(ModelForm):
    benefit_gov_bool = models.CharField(choices=(('False', 0), ('True', 1)))

    class Meta:
        model = SocialDemographicData
        fields = ['profession_txt', 'occupation_txt', 'tv_opt', 'dvd_opt', 'radio_opt', 'bath_opt', 'benefit_gov_bool',
                  'automobile_opt', 'wash_machine_opt', 'refrigerator_opt', 'freezer_opt', 'house_maid_opt'
        ]
        widgets = {
            'profession_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar profissão',
                                         'id': "profession", 'autofocus': True}),
            'occupation_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar ocupação',
                                         'id': "occupation", 'autofocus': True}),
        }


class SocialHistoryDataForm(ModelForm):
    smoker = models.CharField(choices=(('True', 1), ('False', 0)))
    ex_smoker = models.CharField(choices=(('True', 1), ('False', 0)))
    alcoholic = models.CharField(choices=(('True', 1), ('False', 0)))
    #drugs_opt = models.CharField(choices=(('1', 'drugsOption1'), ('2', 'drugsOption2'), ('3', 'drugsOption3')))

    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'ex_smoker', 'alcoholic', 'drugs_opt']