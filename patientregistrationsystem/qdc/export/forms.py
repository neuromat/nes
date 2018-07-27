# coding=utf-8
from django.forms import ModelForm, Form, TextInput, CharField, BooleanField, MultipleChoiceField, \
    CheckboxSelectMultiple, ChoiceField, SelectMultiple, IntegerField, NumberInput, RadioSelect

from django.utils.translation import ugettext_lazy as _


from patient.models import Patient, Diagnosis

HEADINGS_CHOICES = (
    ('code', _("Question code")),
    ('full', _("Full question text")),
    ('abbreviated', _("Abbreviated question text")),
)

RESPONSES_CHOICES = (
    ('short', _("Answer codes")),
    ('long', _("Full answers")),
)


class ExportForm(Form):
    title = CharField(required=False, widget=TextInput(attrs={'class': 'form-control', 'disabled': ''}))
    per_participant = BooleanField(initial=True, required=False)
    per_questionnaire = BooleanField(initial=True, required=False)
    per_eeg_raw_data = BooleanField(initial=True, required=False)
    per_eeg_nwb_data = BooleanField(initial=True, required=False)
    per_emg_data = BooleanField(initial=True, required=False)
    per_tms_data = BooleanField(initial=True, required=False)
    per_additional_data = BooleanField(initial=True, required=False)
    per_goalkeeper_game_data = BooleanField(initial=True, required=False)
    per_stimulus_data = BooleanField(initial=True, required=False)
    per_generic_data = BooleanField(initial=True, required=False)

    questionnaire_entrance_selected = []

    headings = ChoiceField(widget=RadioSelect(), choices=HEADINGS_CHOICES, required=False)
    responses = MultipleChoiceField(widget=CheckboxSelectMultiple(attrs={'data-error': _('Response must be selected')}),
                                    choices=RESPONSES_CHOICES, required=False)


class ParticipantsSelectionForm(ModelForm):

    class Meta:
        model = Patient

        fields = [
            'gender', 'marital_status', 'country', 'city', 'state'
        ]

        widgets = {
            'gender': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
            'marital_status': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
            'country': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
            'state': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
            'city': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
        }

    def __init__(self, *args, **kwargs):
        super(ParticipantsSelectionForm, self).__init__(*args, **kwargs)
        self.fields['gender'].empty_label = None
        self.fields['marital_status'].empty_label = None
        self.fields['country'].empty_label = None
        self.fields['state'].empty_label = None
        self.fields['city'].empty_label = None


class AgeIntervalForm(Form):

    min_age = IntegerField(min_value=0, widget=NumberInput(attrs={'class': 'form-control', 'required': "",
                                                                  'data-error': _('Min age must be filled.'),
                                                                  'disabled': ''}))
    max_age = IntegerField(min_value=0, widget=NumberInput(attrs={'class': 'form-control', 'required': "",
                                                                  'data-error': _('Max age must be filled.'),
                                                                  'disabled': ''}))


class DiagnosisSelectionForm(ModelForm):

    class Meta:
        model = Diagnosis

        fields = ['description']

        widgets = {
            'description': SelectMultiple(attrs={'class': 'form-control', 'required': "", 'disabled': ''}),
        }
