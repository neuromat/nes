# coding=utf-8
from django.forms import ModelForm, Form, TextInput, CharField, BooleanField, MultipleChoiceField, \
    CheckboxSelectMultiple, ValidationError

from django.utils.translation import ugettext as _

FAVORITE_COLORS_CHOICES = (
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('black', 'Black'),
)


class ExportForm(Form):
    title = CharField(required=False, widget=TextInput(attrs={'class': 'form-control', 'disabled': ''}))
    per_participant = BooleanField(initial=True, required=False)
    per_questionnaire = BooleanField(initial=True, required=False)

    questionnaire_entrance_selected = []

    # patient_fields_selected = MultipleChoiceField(required=True,
    #                                               widget=CheckboxSelectMultiple, choices=FAVORITE_COLORS_CHOICES)

    #
    # questionnaire_entrance_fields_selected = []
    #
    # patient_fields_selected = []
    #
    # diagnosis_fields_selected = []
    #
    # per_questionnaire_field = True
    def clean(self):
        cleaned_data = super(ExportForm, self).clean()
        participant_field = cleaned_data.get("per_participant")
        questionnaire_field = cleaned_data.get("per_questionnaire")

        if not (participant_field or questionnaire_field):
            self.add_error('per_participant',
                           _("Either one or both Per participant/Per questionnaire must be set."))
