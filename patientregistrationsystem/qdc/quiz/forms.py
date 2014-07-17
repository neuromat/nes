# coding=utf-8
from django.forms import ModelForm, TextInput, DateInput, Select, RadioSelect, PasswordInput, CheckboxSelectMultiple, \
    CharField, ValidationError
from django.forms.widgets import Textarea
from models import Patient, SocialDemographicData, SocialHistoryData, MedicalRecordData, ComplementaryExam, ExamFile
from django.contrib.auth.hashers import make_password
from quiz_widget import SelectBoxCountries, SelectBoxState

from django.contrib.auth.models import User


class PatientForm(ModelForm):
    class Meta:
        model = Patient

        fields = [
            'cpf_id', 'name_txt', 'number_record', 'rg_id', 'medical_record_number', 'natural_of_txt',
            'citizenship_txt', 'street_txt', 'zipcode_number', 'country_txt', 'state_txt', 'city_txt', 'phone_number',
            'cellphone_number', 'email_txt', 'date_birth_txt', 'gender_opt', 'marital_status_opt',
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
            'email_txt': TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Entrar e-mail', 'id': "email",
                'type': 'email', 'data-error': "E-mail inválido",
                'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
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
                                        )
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
            'social_class_opt': TextInput(attrs={'class': 'form-control', 'id': "social_class_opt", 'disabled': "True"})
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


class MedicalRecordForm(ModelForm):
    class Meta:
        model = MedicalRecordData
        fields = [
            'fracture_history', 'scapula_fracture_side', 'clavicle_fracture_side', 'rib_fracture',
            'cervical_vertebrae_fracture', 'thoracic_vertebrae_fracture', 'lumbosacral_vertebrae_fracture',
            'superior_members_fracture_side', 'inferior_members_fracture_side', 'pelvis_fracture_side',
            'orthopedic_surgery', 'scapula_surgery_side', 'clavicle_surgery_side', 'rib_surgery',
            'cervical_vertebrae_surgery', 'thoracic_vertebrae_surgery', 'lumbosacral_vertebrae_surgery',
            'superior_members_surgery_side', 'inferior_members_surgery_side', 'pelvis_surgery_side',
            'nerve_surgery', 'nerve_surgery_type', 'vertigo_history', 'pain_localizations', 'headache',
            'hypertension', 'diabetes', 'hormonal_dysfunction',
        ]

        widgets = {
            # 'record_date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data',
            #                                 'id': "record_date", "disabled": ""}),
            # 'record_responsible': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar responsável',
            #                                        'id': "record_responsible", "disabled": ""}),
            'fracture_history': RadioSelect(attrs={'id': 'fracture_history'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'scapula_fracture_side': Select(attrs={'class': 'form-control', 'id': 'scapula_fracture_side'}),
            'clavicle_fracture_side': Select(attrs={'class': 'form-control', 'id': 'clavicle_fracture_side'}),
            'rib_fracture': RadioSelect(attrs={'id': 'rib_fracture'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'cervical_vertebrae_fracture': CheckboxSelectMultiple(attrs={'id': 'cervical_vertebrae_fracture'}),
            'thoracic_vertebrae_fracture': CheckboxSelectMultiple(attrs={'id': 'thoracic_vertebrae_fracture'}),
            'lumbosacral_vertebrae_fracture': CheckboxSelectMultiple(attrs={'id': 'lumbosacral_vertebrae_fracture'}),
            'superior_members_fracture_side': Select(attrs={'class': 'form-control',
                                                               'id': 'superior_members_fracture_side'}),
            'inferior_members_fracture_side': Select(attrs={'class': 'form-control',
                                                               'id': 'inferior_members_fracture_side'}),
            'pelvis_fracture_side': Select(attrs={'class': 'form-control', 'id': 'pelvis_fracture_side'}),
            'orthopedic_surgery': RadioSelect(attrs={'id': 'orthopedic_surgery'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'scapula_surgery_side': Select(attrs={'class': 'form-control', 'id': 'scapula_surgery_side'}),
            'clavicle_surgery_side': Select(attrs={'class': 'form-control', 'id': 'clavicle_surgery_side'}),
            'rib_surgery': RadioSelect(attrs={'id': 'rib_surgery'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'cervical_vertebrae_surgery': RadioSelect(attrs={'id': 'cervical_vertebrae_surgery'},
                                                      choices=(('1', 'Sim'), ('0', 'Não'))),
            'thoracic_vertebrae_surgery': RadioSelect(attrs={'id': 'thoracic_vertebrae_surgery'},
                                                      choices=(('1', 'Sim'), ('0', 'Não'))),
            'lumbosacral_vertebrae_surgery': RadioSelect(attrs={'id': 'lumbosacral_vertebrae_surgery'},
                                                         choices=(('1', 'Sim'), ('0', 'Não'))),
            'superior_members_surgery_side': Select(attrs={'class': 'form-control',
                                                              'id': 'superior_members_surgery_side'}),
            'inferior_members_surgery_side': Select(attrs={'class': 'form-control',
                                                              'id': 'inferior_members_surgery_side'}),
            'pelvis_surgery_side': Select(attrs={'class': 'form-control', 'id': 'pelvis_surgery_side'}),
            'nerve_surgery': RadioSelect(attrs={'id': 'nerve_surgery'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'nerve_surgery_type': TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'Entrar tipo de cirurgia de nervo'}),
            'vertigo_history': RadioSelect(attrs={'id': 'vertigo_history'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'pain_localizations': CheckboxSelectMultiple(attrs={'id': 'pain_localizations'}),
            'headache': RadioSelect(attrs={'id': 'headache'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'hypertension': RadioSelect(attrs={'id': 'hypertension'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'diabetes': RadioSelect(attrs={'id': 'diabetes'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'hormonal_dysfunction': RadioSelect(attrs={'id': 'hormonal_dysfunction'},
                                                choices=(('1', 'Sim'), ('0', 'Não'))),
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
            'groups': CheckboxSelectMultiple()
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
                                               'id': "exam_date", 'required': "",
                                               'data-error': "Data deve ser preenchida"},
                                        ),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição', 'cols': '100'}),
            'doctor': TextInput(attrs={'class': 'form-control', 'placeholder': 'Médico'}),
            'doctor_register': TextInput(attrs={'class': 'form-control', 'placeholder': 'CRM'}),
            'exam_site': TextInput(attrs={'class': 'form-control', 'placeholder': 'Local de realização'}),
        }


class ExamFileForm(ModelForm):
    class Meta:
        model = ExamFile
        fields = ['content']
