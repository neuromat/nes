# coding=utf-8
#from django.utils.six import attr
from django.forms import ModelForm, TextInput, DateInput
from models import Patient, SocialDemographicData, SocialHistoryData
from django.db import models
from quiz_widget import SelectBoxCountries, SelectBoxState
from django.forms.widgets import Select, RadioSelect


class PatientForm(ModelForm):
    class Meta:
        model = Patient
        fields = [
            'cpf_id', 'name_txt', 'rg_id', 'medical_record_number', 'natural_of_txt', 'citizenship_txt', 'street_txt',
            'zipcode_number', 'country_txt', 'state_txt', 'city_txt', 'phone_number', 'cellphone_number', 'email_txt',
            'date_birth_txt', 'gender_opt', 'marital_status_opt',
        ]
        widgets = {
            'name_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome completo',
                                         'id': "full_name", 'autofocus': "true", 'required': "",
                                         'data-error': "Nome deve ser preenchido"}),
            'cpf_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CPF',
                                       'id': "cpf_id"}),
            'rg_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar RG', 'id': "rg_id"}),
            'natural_of_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar Naturalidade',
                                               'id': "naturalOf"}),
            'street_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua - Complemento',
                                           'id': "street_txt"}),
            'zipcode_number': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Entrar CEP', 'id': "zipcode",
                       'data-error': "CEP inválido", 'pattern': '\d{5}-?\d{3}'}),
            'city_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar cidade', 'id': "city"}),
            'phone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar telefone para contato',
                                             'id': "phone"}),
            'cellphone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar celular',
                                                 'id': "cellphone"}),
            'email_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar e-mail', 'id': "email",
                                          'type': 'email', 'data-error': "E-mail inválido",
                                          'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'
                                }),
            'medical_record_number': TextInput(attrs={'class': 'form-control',
                                                      'placeholder': 'Entrar número do prontuário',
                                                      'id': "records_number"}),
            'citizenship_txt': SelectBoxCountries(attrs={'id': 'id_chosen_country', 'data-flags': 'true'}),
            'country_txt': SelectBoxCountries(attrs={'id': 'id_country_state_address', 'data-flags': 'true'}),
            'state_txt': SelectBoxState(attrs={'data-country': 'id_country_state_address', 'id': 'id_chosen_state'}),
            'gender_opt': Select(attrs={'class': 'form-control', 'id': 'gender_id', 'required': "",
                                        'data-error': "Sexo deve ser preenchido"}),
            'marital_status_opt': Select(attrs={'class': 'form-control', 'id': 'marital_status'}),
            'date_birth_txt': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data',
                                               'id': "birthday", 'required': "",
                                               'data-error': "Data de nascimento deve ser preenchida"},
                                        format='%Y-%m-%d')
        }
        error_messages = {
            'name_txt': {
                'required': 'Nome não preenchido'
            }
        }


class SocialDemographicDataForm(ModelForm):
    class Meta:
        model = SocialDemographicData
        fields = ['profession_txt', 'occupation_txt', 'tv_opt', 'dvd_opt', 'radio_opt', 'bath_opt',
                  'automobile_opt', 'wash_machine_opt', 'refrigerator_opt', 'freezer_opt', 'house_maid_opt',
                  'religion_opt', 'payment_opt', 'flesh_tone_opt', 'schooling_opt', 'benefit_government_bool',
                  ]
        widgets = {
            'benefit_government_bool': RadioSelect(attrs={'id': 'id_benefit'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'schooling_opt': Select(attrs={'class': 'form-control', 'id': 'scolarity'}),
            'flesh_tone_opt': Select(attrs={'class': 'form-control', 'id': 'skin_color'}),
            'religion_opt': Select(attrs={'class': 'form-control', 'id': 'religion_id'}),
            'profession_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar profissão',
                                               'id': "profession"}),
            'occupation_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar ocupação',
                                               'id': "occupation"}),
            'payment_opt': Select(attrs={'class': 'form-control', 'id': 'payment_id'}),
            'tv_opt': RadioSelect(attrs={'id': 'id_tv_opt'},
                                  choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'dvd_opt': RadioSelect(attrs={'id': 'id_dvd_opt'},
                                   choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'radio_opt': RadioSelect(attrs={'id': 'id_radio_opt'},
                                     choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'bath_opt': RadioSelect(attrs={'id': 'id_bath_opt'},
                                    choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'automobile_opt': RadioSelect(attrs={'id': 'id_automobile_opt'},
                                          choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'house_maid_opt': RadioSelect(attrs={'id': 'id_house_maid_opt'},
                                          choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'wash_machine_opt': RadioSelect(attrs={'id': 'id_wash_machine_opt'},
                                            choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'refrigerator_opt': RadioSelect(attrs={'id': 'id_refrigerator_opt'},
                                            choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'freezer_opt': RadioSelect(attrs={'id': 'id_freezer_opt'},
                                       choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
        }


class SocialHistoryDataForm(ModelForm):
    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'amount_cigarettes_opt', 'ex_smoker', 'alcoholic', 'alcohol_frequency_opt',
                  'alcohol_period_opt', 'drugs_opt', ]

        widgets = {
            'smoker': RadioSelect(attrs={'id': 'id_smoker'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'amount_cigarettes_opt': Select(attrs={'class': 'form-control', 'id': 'id_amount_cigarettes'}),
            'ex_smoker': RadioSelect(attrs={'id': 'id_ex_smoker'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'alcoholic': RadioSelect(attrs={'id': 'id_alcoholic'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'alcohol_frequency_opt': Select(attrs={'class': 'form-control', 'id': 'id_freqSmok'}),
            'alcohol_period_opt': Select(attrs={'class': 'form-control', 'id': 'id_periodSmok'}),
            'drugs_opt': RadioSelect(attrs={'id': 'id_drugs_opt'},
                                     choices=(('ja_fez', 'Já fez'), ('faz', 'Faz'), ('nunca_fez', 'Nunca fez'))),
        }
