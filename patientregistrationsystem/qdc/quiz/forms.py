# coding=utf-8
from django.forms import ModelForm, TextInput, DateInput, Select, RadioSelect, PasswordInput, CheckboxSelectMultiple, \
    CharField, ValidationError
from django.forms.widgets import Textarea
from quiz.models import Patient, SocialDemographicData, SocialHistoryData, ComplementaryExam, ExamFile
from django.contrib.auth.hashers import make_password
from quiz.quiz_widget import SelectBoxCountries, SelectBoxState
from cep.widgets import CEPInput
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

# pylint: disable=E1101
# pylint: disable=E1103


class PatientForm(ModelForm):
    class Meta:
        model = Patient

        fields = [
            'cpf', 'name', 'rg', 'medical_record', 'natural_of','citizenship', 'zipcode', 'street', 'city', 'state',
            'country', 'phone', 'cellphone', 'email', 'date_birth', 'gender', 'marital_status', 'district',
            'address_complement', 'address_number'
        ]

        widgets = {
            'zipcode': CEPInput(address={'street': 'id_street', 'district': 'id_district', 'city': 'id_city',
                                         'state': 'id_state'},
                                       attrs={'class': 'form-control', 'pattern': '\d{5}-?\d{3}'}),
            'street': TextInput(attrs={'class': 'form-control'}),
            'address_number': TextInput(attrs={'class': 'form-control'}),
            'address_complement': TextInput(attrs={'class': 'form-control'}),
            'district': TextInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'state': SelectBoxState(attrs={'data-country': 'id_country'}),
            'country': SelectBoxCountries(attrs={'data-flags': 'true'}),
            'name': TextInput(attrs={'class': 'form-control', 'autofocus': "true", 'required': "",
                                     'data-error': _('Nome deve ser preenchido')}),
            'cpf': TextInput(attrs={'class': 'form-control'}),
            'rg': TextInput(attrs={'class': 'form-control'}),
            'natural_of': TextInput(attrs={'class': 'form-control'}),
            'phone': TextInput(attrs={'class': 'form-control'}),
            'cellphone': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control', 'type': 'email', 'data-error': _('E-mail incorreto'),
                                      'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
            'medical_record': TextInput(attrs={'class': 'form-control'}),
            'citizenship': SelectBoxCountries(attrs={'data-flags': 'true'}),
            'gender': Select(attrs={'class': 'form-control', 'required': "",
                                    'data-error': _('Sexo deve ser preenchido')}),
            'marital_status': Select(attrs={'class': 'form-control'}),
            'date_birth': DateInput(attrs={'class': 'form-control', 'required': "",
                                           'data-error': _('Data de nascimento deve ser preenchida')})
        }


class SocialDemographicDataForm(ModelForm):
    class Meta:
        model = SocialDemographicData
        fields = ['profession', 'occupation', 'tv', 'dvd', 'radio', 'bath',
                  'automobile', 'wash_machine', 'refrigerator', 'freezer', 'house_maid',
                  'religion', 'payment', 'flesh_tone', 'schooling', 'benefit_government',
                  'social_class']
        widgets = {
            'benefit_government': RadioSelect(choices=(('1', 'Sim'), ('0', 'Não'))),
            'schooling': Select(attrs={'class': 'form-control'}),
            'flesh_tone': Select(attrs={'class': 'form-control'}),
            'religion': Select(attrs={'class': 'form-control'}),
            'profession': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar profissão'}),
            'occupation': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar ocupação'}),
            'payment': Select(attrs={'class': 'form-control'}),
            'tv': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'dvd': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'radio': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'bath': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'automobile': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'house_maid': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'wash_machine': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'refrigerator': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'freezer': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4 ou +'))),
            'social_class': TextInput(attrs={'class': 'form-control', 'readonly': ""})
        }


class SocialHistoryDataForm(ModelForm):
    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'amount_cigarettes', 'ex_smoker', 'alcoholic', 'alcohol_frequency',
                  'alcohol_period', 'drugs', ]

        widgets = {
            'smoker': RadioSelect(attrs={'id': 'id_smoker'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'amount_cigarettes': Select(attrs={'class': 'form-control'}),
            'ex_smoker': RadioSelect(choices=(('1', 'Sim'), ('0', 'Não'))),
            'alcoholic': RadioSelect(attrs={'id': 'id_alcoholic'}, choices=(('1', 'Sim'), ('0', 'Não'))),
            'alcohol_frequency': Select(attrs={'class': 'form-control'}),
            'alcohol_period': Select(attrs={'class': 'form-control'}),
            'drugs': RadioSelect(choices=(('ja_fez', 'Já fez'), ('faz', 'Faz'), ('nunca_fez', 'Nunca fez'))),
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
