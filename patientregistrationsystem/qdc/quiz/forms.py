# coding=utf-8
from django.forms import ModelForm, TextInput
from models import Patient, SocialDemographicData, SocialHistoryData
from django.db import models

# Create the form class.
class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = [
            'cpf_id', 'name_txt', 'rg_id', 'medical_record_number','natural_of_txt', 'citizenship_txt', 'street_txt',
            'zipcode_number', 'country_txt', 'state_txt', 'city_txt', 'phone_number', 'cellphone_number', 'email_txt',
            'dt_birth_txt'
        ]
        widgets = {
            'name_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome completo',
                                         'id': "full_name", 'autofocus': True}),
            'cpf_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CPF',
                                         'id': "cpf_id", 'autofocus': True}),
            'rg_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar RG',
                                         'id': "rg_id", 'autofocus': True}),
            'natural_of_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar Naturalidade',
                                         'id': "naturalOf", 'autofocus': True}),
            'street_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua - Complemento',
                                         'id': "street_txt", 'autofocus': True}),
            'zipcode_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CEP',
                                         'id': "zipcode", 'autofocus': True}),
            'city_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar cidade',
                                         'id': "city", 'autofocus': True}),
            'phone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar telefone para contato',
                                         'id': "phone", 'autofocus': True}),
            'cellphone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar celular',
                                         'id': "cellphone", 'autofocus': True}),
            'email_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar e-mail',
                                         'id': "email", 'autofocus': True}),
            'medical_record_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar número do prontuário',
                                         'id': "records_number", 'autofocus': True}),


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
    #int sum_opt
    #tv_opt = models.IntegerField(choices=((0, 'TVoption0'), (1, 'TVoption1'), (2, 'TVoption2'), (3, 'TVoption3'),\
    # (4, 'TVoption4')))
    #dvd_opt = models.IntegerField(choices=((0, 'DVDoption0'), (1, 'DVDoption1'), (2, 'DVDoption2'), (3, 'DVDoption3'),\
    # (4, 'DVDoption4')))
    #radio_opt = choices=((0, 'RADIOoption0'), (1, 'RADIOoption1'), (2, 'RADIOoption2'), (3, 'RADIOoption3'),\
    # (4, 'RADIOoption4'))
    #bath_opt = choices=((0, 'Bathsoption0'), (1, 'Bathsoption1'), (2, 'Bathsoption2'), (3, 'Bathsoption3'),\
    #  (4, 'Bathsoption4'))
    #auto_opt = choices=((0, 'Autooption0'), (1, 'Autooption1'), (2, 'Autooption2'), (3, 'Autooption3'),\
    #  (4, 'Autooption4'))
    #wm_opt = choices=((0, 'WMoption0'), (1, 'WMoption1'), (2, 'WMoption2'), (3, 'WMoption3'), (4, 'WMoption4'))
    #refrigerator_opt = choices=((0, 'Refrigoption0'), (1, 'Refrigoption1'), (2, 'Refrigoption2'),\
    #  (3, 'Refrigoption3'), (4, 'Refrigoption4'))
    #freezer_opt = (0, 'Freezoption0'), (1, 'Freezoption1'), (2, 'Freezoption2'), (3, 'Freezoption3'),\
    #  (4, 'Freezoption4'))
    #house_maid_opt = choices=((0, 'Employoption0'), (1, 'Employoption1'), (2, 'Employoption2'), (3, 'Employoption3'),\
    #  (4, 'Employoption4'))
    #sum_opt = tv_opt +
    #social_class_opt = models.CharField(choices=(('A1', 42-46))))
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