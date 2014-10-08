# coding=utf-8
from django.forms import ModelForm, TextInput, DateInput, Select, RadioSelect
from django.forms.widgets import Textarea
from cep.widgets import CEPInput
from django.utils.translation import ugettext_lazy as _

from patient.models import Patient, SocialDemographicData, SocialHistoryData, ComplementaryExam, ExamFile
from patient.quiz_widget import SelectBoxCountries, SelectBoxState



# pylint: disable=E1101
# pylint: disable=E1103


class PatientForm(ModelForm):
    class Meta:
        model = Patient

        fields = [
            'cpf', 'name', 'rg', 'medical_record', 'natural_of', 'citizenship', 'zipcode', 'street', 'city', 'state',
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


class ComplementaryExamForm(ModelForm):
    class Meta:
        model = ComplementaryExam
        fields = ['date', 'description', 'doctor', 'doctor_register', 'exam_site']

        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'required': "",
                                     'data-error': "Data deve ser preenchida"}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição', 'rows': '4',
                                           'required': "", 'data-error': "Descrição deve ser preenchida"}),
            'doctor': TextInput(attrs={'class': 'form-control', 'placeholder': 'Médico'}),
            'doctor_register': TextInput(attrs={'class': 'form-control', 'placeholder': 'CRM'}),
            'exam_site': TextInput(attrs={'class': 'form-control', 'placeholder': 'Local de realização'}),
        }


class ExamFileForm(ModelForm):
    class Meta:
        model = ExamFile
        fields = ['content']
