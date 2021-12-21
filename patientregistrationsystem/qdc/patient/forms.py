# -*- coding: UTF-8 -*-
from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, TextInput, DateInput, Select, RadioSelect, TypedChoiceField
from django.forms.widgets import Textarea

from patient.models import Patient, Telephone, SocialDemographicData, SocialHistoryData, ComplementaryExam, ExamFile, \
    QuestionnaireResponse

# pylint: disable=E1101
# pylint: disable=E1103


class PatientForm(ModelForm):
    def __init__(self, data=None, *args, **kwargs):
        super(PatientForm, self).__init__(data, *args, **kwargs)
        self.fields['zipcode'].widget.attrs['onBlur'] = 'pesquisacep(this.value);'
        self.fields['country'].initial = 'BR'

    anonymous = forms.BooleanField(required=False,
                                   initial=False,
                                   label=_('Anonymous participant?'))

    class Meta:
        model = Patient

        fields = [
            'anonymous', 'name', 'cpf', 'origin', 'medical_record', 'date_birth', 'gender', 'rg', 'marital_status',
            'country', 'zipcode', 'street', 'address_number', 'address_complement', 'district', 'city', 'state', 'email'
        ]

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'autofocus': "true", 'required': "",
                                     'data-error': _('Name must be included')}),
            'cpf': TextInput(attrs={'class': 'form-control',
                                    'placeholder': 'xxx.xxx.xxx-xx'}),
            'origin': TextInput(attrs={'class': 'form-control'}),
            'medical_record': TextInput(attrs={'class': 'form-control'}),
            'date_birth': DateInput(format=_("%m/%d/%Y"), attrs={'class': 'form-control datepicker', 'required': "",
                                                                 'placeholder': _('mm/dd/yyyy'),
                                                                 'data-error': _('Date of birth must be completed')}),
            'gender': Select(attrs={'class': 'form-control', 'required': "",
                                    'data-error': _('Gender must be filled')}),
            'rg': TextInput(attrs={'class': 'form-control'}),
            'marital_status': Select(attrs={'class': 'form-control'}),

            'country': Select(attrs={'class': 'form-control'}),
            'zipcode': TextInput(attrs={'class': 'form-control', 'pattern': '\d{5}-?\d{3}'}),
            'street': TextInput(attrs={'class': 'form-control'}),
            'address_number': TextInput(attrs={'class': 'form-control'}),
            'address_complement': TextInput(attrs={'class': 'form-control'}),
            'district': TextInput(attrs={'class': 'form-control'}),
            'city': TextInput(attrs={'class': 'form-control'}),
            'state': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={
                'class': 'form-control', 'type': 'email', 'data-error': _('Incorrect e-mail'),
                'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
        }

    # Make the name required if anonymous field is not checked
    def clean(self):
        anonymous = self.cleaned_data.get('anonymous', False)
        if not anonymous:
            # validate the name
            name = self.cleaned_data.get('name', None)
            if name in EMPTY_VALUES:
                self._errors['name'] = self.error_class([_('Name must be included')])
        return self.cleaned_data


class TelephoneForm(ModelForm):
    class Meta:
        model = Telephone

        fields = ['number', 'type', 'note']

        widgets = {
            'number': TextInput(attrs={'class': 'form-control telephone_number', 'pattern': '^[- ()0-9]+'}),
            'type': Select(attrs={'class': 'form-control'}),
            'note': TextInput(attrs={'class': 'form-control'})
        }


class SocialDemographicDataForm(ModelForm):
    benefit_government = TypedChoiceField(required=False,
                                          empty_value=None,
                                          choices=((True, _("Yes")), (False, _("No"))),
                                          widget=RadioSelect)

    class Meta:
        model = SocialDemographicData
        fields = ['natural_of', 'citizenship', 'profession', 'occupation', 'tv', 'dvd', 'radio', 'bath',
                  'automobile', 'wash_machine', 'refrigerator', 'freezer', 'house_maid',
                  'religion', 'payment', 'flesh_tone', 'patient_schooling', 'schooling', 'benefit_government',
                  'social_class']
        widgets = {
            'natural_of': TextInput(attrs={'class': 'form-control'}),
            'citizenship': Select(attrs={'class': 'form-control'}),
            'patient_schooling': Select(attrs={'class': 'form-control'}),
            'schooling': Select(attrs={'class': 'form-control'}),
            'flesh_tone': Select(attrs={'class': 'form-control'}),
            'religion': Select(attrs={'class': 'form-control'}),
            'profession': TextInput(attrs={'class': 'form-control', 'placeholder': _('Type in profession')}),
            'occupation': TextInput(attrs={'class': 'form-control', 'placeholder': _('Inform occupation')}),
            'payment': Select(attrs={'class': 'form-control'}),
            'tv': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'dvd': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'radio': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'bath': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'automobile': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'house_maid': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'wash_machine': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'refrigerator': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'freezer': RadioSelect(choices=((0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, _('4 or +')))),
            'social_class': TextInput(attrs={'class': 'form-control', 'readonly': ""})
        }


class SocialHistoryDataForm(ModelForm):
    smoker = TypedChoiceField(required=False,
                              empty_value=None,
                              choices=((True, _("Yes")), (False, _("No"))),
                              widget=RadioSelect(attrs={'id': 'id_smoker'}))
    ex_smoker = TypedChoiceField(required=False,
                                 empty_value=None,
                                 choices=((True, _("Yes")), (False, _("No"))),
                                 widget=RadioSelect)
    alcoholic = TypedChoiceField(required=False,
                                 empty_value=None,
                                 choices=((True, _("Yes")), (False, _("No"))),
                                 widget=RadioSelect(attrs={'id': 'id_alcoholic'}))

    class Meta:
        model = SocialHistoryData
        fields = ['smoker', 'amount_cigarettes', 'ex_smoker', 'alcoholic', 'alcohol_frequency',
                  'alcohol_period', 'drugs', ]

        widgets = dict(amount_cigarettes=Select(attrs={'class': 'form-control'}),
                       alcohol_frequency=Select(attrs={'class': 'form-control'}),
                       alcohol_period=Select(attrs={'class': 'form-control'}),
                       drugs=RadioSelect(choices=(('ja_fez', _("Have already used")), ('faz', _('It is using')),
                                                  ('nunca_fez', _('Have never used')))))


class ComplementaryExamForm(ModelForm):
    class Meta:
        model = ComplementaryExam
        fields = ['date', 'description', 'doctor', 'doctor_register', 'exam_site']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "", 'data-error': _("Date must be completed")}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': _('Description'), 'rows': '4',
                                           'required': "", 'data-error': _("Description must be filled in")}),
            'doctor': TextInput(attrs={'class': 'form-control', 'placeholder': _('Doctor')}),
            'doctor_register': TextInput(attrs={'class': 'form-control', 'placeholder': _('CRM')}),
            'exam_site': TextInput(attrs={'class': 'form-control', 'placeholder': _('Place of execution')}),
        }


class ExamFileForm(ModelForm):
    class Meta:
        model = ExamFile
        fields = ['content']


class QuestionnaireResponseForm(ModelForm):
    class Meta:
        model = QuestionnaireResponse
        fields = ['date']

        widgets = {
            'date': DateInput(
                format=_("%m/%d/%Y"),
                attrs={'class': 'form-control datepicker',
                       'placeholder': _('mm/dd/yyyy'), 'required': '',
                       'data-error': _('Fill date must be filled.')},
            )
        }
