from models import Experiment, Questionnaire
from django.forms import ModelForm, TextInput, DateInput


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['title', 'description', 'start_date', 'end_date', 'eci_software']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar titulo',
                                      'id': "experiment_title"}),
            'description': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar descrição',
                                            'id': 'experiment_description'}),
            'start_date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'id': 'start_date'}),
            'end_date': DateInput(attrs={'class': 'form-control', 'placeholder': 'Data', 'id': 'end_date'}),
            'eci_software': TextInput(attrs={'class': 'form-control', 'placeholder': 'eci-software',
                                             'id': 'eci_software'})
        }


class QuestionnaireForm(ModelForm):
    class Meta:
        model = Questionnaire
        fields = ['sid']

        widgets = {
            'sid': TextInput(attrs={'class': 'form-control', 'placeholder': 'SID', 'id': 'survey_id'})
        }