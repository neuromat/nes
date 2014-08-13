# coding=utf-8
from models import Experiment, Questionnaire
from django.forms import ModelForm, TextInput, Textarea


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        # fields = ['title', 'description', 'start_date', 'end_date', 'eci_software']
        fields = ['title', 'description', 'questionnaires']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Entrar titulo',
                                      'id': "experiment_title"}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Entrar descrição',
                                           'rows': '4', 'id': 'experiment_description'}),
            # 'start_date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'id': 'start_date'}),
            # 'end_date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'id': 'end_date'}),
            # 'eci_software': TextInput(attrs={'class': 'form-control', 'placeholder': 'eci-software',
            #                                  'id': 'eci_software'})
        }


class QuestionnaireForm(ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['survey_id']

        widgets = {
            'survey_id': TextInput(attrs={'class': 'form-control', 'placeholder': 'SID', 'id': 'survey_id'})
        }