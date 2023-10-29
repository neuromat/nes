# coding=utf-8
from django.forms import CharField, ModelForm, CheckboxInput, TextInput

from .models import Survey


class SurveyForm(ModelForm):
    title = CharField(
        required=False,
        widget=TextInput(attrs={"class": "form-control", "disabled": ""}),
    )

    class Meta:
        model = Survey

        fields = ["is_initial_evaluation"]

        widgets = {
            "is_initial_evaluation": CheckboxInput(attrs={"class": "form-check-input"}),
        }
