# coding=utf-8
from models import Experiment, Questionnaire
from django.forms import ModelForm, TextInput, Textarea


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Entrar titulo',
                                      'id': "experiment_title"}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Entrar descrição',
                                           'rows': '4', 'id': 'experiment_description'}),
        }


# class QuestionnaireForm(ModelForm):
#     class Meta:
#         model = Questionnaire
#         fields = ['survey_id']
#
#         widgets = {
#             'survey_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'SID', 'id': 'survey_id'})
#         }
