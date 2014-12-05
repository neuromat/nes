# coding=utf-8
from experiment.models import Experiment, QuestionnaireConfiguration, QuestionnaireResponse, SubjectOfGroup, Group, \
    Component, Task, Stimulus, Pause, Sequence, Questionnaire, ComponentConfiguration
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, CheckboxInput, BooleanField
# from datetimewidget.widgets import DateTimeWidget


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': 'Título deve ser preenchido.'}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': 'Descrição deve ser preenchida.'}),
        }


class GroupForm(ModelForm):
    class Meta:

        model = Group

        fields = ['title', 'description', 'instruction']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': 'Título deve ser preenchido.'}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '2', 'required': "",
                                           'data-error': 'Descrição deve ser preenchida.',
                                           'maxlength': '150'}),
            'instruction': Textarea(attrs={'class': 'form-control',
                                           'rows': '2', 'required': "",
                                           'data-error': 'Descrição deve ser preenchida.',
                                           'maxlength': '150'}),
        }


class QuestionnaireConfigurationForm(ModelForm):
    class Meta:
        model = QuestionnaireConfiguration
        fields = ['number_of_fills', 'interval_between_fills_value', 'interval_between_fills_unit']

        widgets = {
            'number_of_fills': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Quantidade deve ser preenchida.'}),
            'interval_between_fills_value': TextInput(attrs={'class': 'form-control', 'required': "",
                                                             'data-error': 'Intervalo deve ser preenchido.'}),
            'interval_between_fills_unit': Select(attrs={'class': 'form-control', 'required': "",
                                                         'data-error': "Unidade deve ser preenchida"}),
        }


class QuestionnaireResponseForm(ModelForm):
    class Meta:
        model = QuestionnaireResponse
        fields = [
            'date',
        ]

        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/aaaa', 'required': "",
                                     'data-error': "Data de preenchimento deve ser preenchida"}, )
        }


class FileForm(ModelForm):
    class Meta:
        model = SubjectOfGroup
        fields = ['consent_form']


class ComponentForm(ModelForm):
    class Meta:
        model = Component
        fields = ['identification', 'description']

        widgets = {
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Identificação deve ser preenchida.'}),
            'description': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Descrição deve ser preenchida.'})
        }


class ComponentConfigurationForm(ModelForm):
    class Meta:
        model = ComponentConfiguration
        fields = ['name', 'number_of_repetitions', 'interval_between_repetitions_value',
                  'interval_between_repetitions_unit']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Nome deve ser preenchido.'}),
            'number_of_repetitions': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Número de repetições deve ser preenchida.'}),
            'interval_between_repetitions_value': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Intervalo deve ser preenchido.'}),
            'interval_between_repetitions_unit': Select(attrs={'class': 'form-control', 'required': "",
                                                         'data-error': "Unidade deve ser preenchida"}),
        }


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['instruction']

        widgets = {
            'instruction': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Instrução deve ser preenchida.'})
        }


class StimulusForm(ModelForm):
    class Meta:
        model = Stimulus
        fields = ['stimulus_type']

        widgets = {
            'stimulus_type': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Tipo do estímulo deve ser preenchido.'})
        }


class PauseForm(ModelForm):
    class Meta:
        model = Pause
        fields = ['duration', 'duration_unit']

        widgets = {
            'duration': TextInput(attrs={'class': 'form-control', 'required': "",
                                         'data-error': 'Duração da pausa deve ser preenchida.'}),
            'duration_unit': Select(attrs={'class': 'form-control', 'required': "",
                                                         'data-error': "Unidade deve ser preenchida"}),
        }


class SequenceForm(ModelForm):
    class Meta:
        model = Sequence
        fields = ['has_random_components', 'number_of_mandatory_components']

        widgets = {
            'number_of_mandatory_components': TextInput(attrs={'class': 'form-control', 'required': "",
                                                'data-error': 'Quantidade deve ser preenchida.'}),
        }
