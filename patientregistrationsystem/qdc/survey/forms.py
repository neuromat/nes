# coding=utf-8
from django.forms import ModelForm, TextInput, CharField

from .models import Survey


class SurveyForm(ModelForm):

    title = CharField(required=False, widget=TextInput(attrs={'class': 'form-control', 'disabled': ''}))

    class Meta:
        model = Survey

        fields = ['is_initial_evaluation']
