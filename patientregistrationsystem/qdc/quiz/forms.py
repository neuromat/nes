# coding=utf-8
from django.forms import ModelForm, TextInput, DateInput, Select, RadioSelect, PasswordInput, CheckboxSelectMultiple, \
    CharField, ValidationError
from django.forms.widgets import Textarea
from models import Patient, SocialDemographicData, SocialHistoryData, ComplementaryExam, ExamFile
from django.contrib.auth.hashers import make_password
from quiz_widget import SelectBoxCountries, SelectBoxState
from cep.widgets import CEPInput

from django.contrib.auth.models import User

# pylint: disable=E1101
# pylint: disable=E1103

STATE = (('AA', ''), ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
         ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
         ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
         ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
         ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
         ('SE', 'Sergipe'), ('TO', 'Tocantins'))

class PatientForm(ModelForm):
    class Meta:
        model = Patient

        fields = [
            'cpf_id', 'name_txt', 'number_record', 'rg_id', 'medical_record_number', 'natural_of_txt',
            'citizenship_txt', 'zipcode_number', 'street_txt', 'city_txt', 'state_txt', 'country_txt', 'phone_number',
            'cellphone_number', 'email_txt', 'date_birth_txt', 'gender_opt', 'marital_status_opt', 'district',
            'complement', 'number'
        ]

        widgets = {
            'zipcode_number': CEPInput(address={'street': 'street_txt', 'district': 'district', 'city': 'city',
                                                'state': 'id_chosen_state'},
                                       attrs={'class': 'form-control', 'placeholder': 'Digite o CEP', 'pattern': '\d{5}-?\d{3}'}),
            'street_txt': TextInput(attrs={'class': 'form-control', 'id': "street_txt"}),
            'number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Número Residencial', 'id': "number"}),
            'complement': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar Complemento', 'id': "complement"}),
            'district': TextInput(attrs={'class': 'form-control', 'id': "district"}),
            'city_txt': TextInput(attrs={'class': 'form-control', 'id': "city"}),
            'state_txt': Select(attrs={'class': 'form-control', 'id': 'id_chosen_state'}, choices = STATE),
            'country_txt': SelectBoxCountries(attrs={'id': 'id_country_state_address', 'data-flags': 'true'}),
            'name_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome completo',
                                         'id': "full_name", 'autofocus': "true", 'required': "",
                                         'data-error': "Nome deve ser preenchido"}),
            'cpf_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar CPF',
                                       'id': "cpf_id"}),
            'rg_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar RG', 'id': "rg_id"}),
            'natural_of_txt': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar Naturalidade',
                                               'id': "naturalOf"}),
            'phone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar telefone para contato',
                                             'id': "phone"}),
            'cellphone_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar celular',
                                                 'id': "cellphone"}),
            'email_txt': TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Entrar e-mail', 'id': "email",
                'type': 'email', 'data-error': "E-mail inválido",
                'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
            'medical_record_number': TextInput(attrs={'class': 'form-control',
                                                      'placeholder': 'Entrar número do prontuário',
                                                      'id': "records_number"}),
            'citizenship_txt': SelectBoxCountries(attrs={'id': 'id_chosen_country', 'data-flags': 'true'}),
            'gender_opt': Select(attrs={'class': 'form-control', 'id': 'gender_id', 'required': "",
                                        'data-error': "Sexo deve ser preenchido"}),
            'marital_status_opt': Select(attrs={'class': 'form-control', 'id': 'marital_status'}),
            'date_birth_txt': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data',
                                               'id': "birthday", 'required': "",
                                               'data-error': "Data de nascimento deve ser preenchida"}, )
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
                  'social_class_opt']
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
            'social_class_opt': TextInput(attrs={'class': 'form-control', 'id': "social_class_opt", 'readonly': ""})
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


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'groups']

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar primeiro nome'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar último nome'}),
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome de usuário'}),
            'password': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha',
                                             'onkeyup': "password_strong(); if(beginCheckPassword1)checkPass();"}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar e-mail', 'id': "email",
                                      'type': 'email', 'data-error': "E-mail inválido",
                                      'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]' +
                                                 '+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
            'groups': CheckboxSelectMultiple(),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if not self.instance.pk and User.objects.filter(username=username):
            raise ValidationError(u'Este nome de usuário já existe.')
        return username

    def clean_password(self):
        return make_password(self.cleaned_data['password'])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email, is_active=True).exclude(username=username).count():
            raise ValidationError(u'Este email já existe.')
        return email


class UserFormUpdate(UserForm):
    password = CharField(required=False,
                         widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha',
                                                     'onkeyup': "password_strong();"
                                                                "if(beginCheckPassword1)checkPass();"}))

    def clean_password(self):
        if self.cleaned_data['password']:
            return make_password(self.cleaned_data['password'])
        else:
            return self.instance.password


class ComplementaryExamForm(ModelForm):
    class Meta:
        model = ComplementaryExam
        fields = ['date', 'description', 'doctor', 'doctor_register', 'exam_site']

        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data',
                                     'id': 'exam_date', 'required': "",
                                     'data-error': "Data deve ser preenchida"}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição',
                                           'rows': '4', 'id': 'exam_description', 'required': "",
                                           'data-error': "Descrição deve ser preenchida"}),
            'doctor': TextInput(attrs={'class': 'form-control', 'placeholder': 'Médico'}),
            'doctor_register': TextInput(attrs={'class': 'form-control', 'placeholder': 'CRM'}),
            'exam_site': TextInput(attrs={'class': 'form-control', 'placeholder': 'Local de realização'}),
        }


class ExamFileForm(ModelForm):
    class Meta:
        model = ExamFile
        fields = ['content']
