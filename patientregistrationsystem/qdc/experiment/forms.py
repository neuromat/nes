# coding=utf-8
from models import Experiment, Questionnaire
from django.forms import ModelForm, TextInput, Textarea, Select


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


class QuestionnaireForm(ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['number_of_fills', 'interval_between_fills_value', 'interval_between_fills_unit']

        widgets = {
            'number_of_fills': TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'Quantidade de prenchimentos',
                                                'id': "number_of_fills",
                                                'required': ""}),
            'interval_between_fills_value': TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Intervalo entre prenchimentos',
                                                             'id': "interval_between_fills_value",
                                                             'required': ""}),
            'interval_between_fills_unit': Select(attrs={'class': 'form-control',
                                                         'id': 'interval_between_fills_unit',
                                                         'required': "",
                                                         'data-error': "Unidade deve ser preenchida"}),
        }
