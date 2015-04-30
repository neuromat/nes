# coding=utf-8
from experiment.models import Experiment, QuestionnaireConfiguration, QuestionnaireResponse, SubjectOfGroup, Group, \
    Component, Task, Stimulus, Pause, Block, Instruction, ComponentConfiguration, ResearchProject
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, TypedChoiceField, RadioSelect


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['research_project', 'title', 'description']

        widgets = {
            'research_project': Select(attrs={'class': 'form-control'}, choices='research_projects'),
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

        fields = ['title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': 'Título deve ser preenchido.'}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '2', 'required': "",
                                           'data-error': 'Descrição deve ser preenchida.',
                                           'maxlength': '150'})
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
            'date': DateInput(attrs={'class': 'form-control datepicker', 'placeholder': 'dd/mm/aaaa', 'required': "",
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
            # Even though maxlength is already set in the model, it has be be repeated here, because the form dos not
            # respect that information.
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'maxlength': '1500'}),
        }


class ComponentConfigurationForm(ModelForm):
    # This is required because will be included only when the parent is a sequence.
    random_position = TypedChoiceField(required=False,
                                       empty_value=None,
                                       choices=((False, 'Fixa'), (True, 'Aleatória')),
                                       widget=RadioSelect(attrs={'id': 'id_random_position'}))

    class Meta:
        model = ComponentConfiguration
        fields = ['name', 'random_position', 'number_of_repetitions', 'interval_between_repetitions_value',
                  'interval_between_repetitions_unit']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
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
        fields = ['instruction_text']

        widgets = {
            'instruction_text': TextInput(attrs={'class': 'form-control', 'required': "",
                                                 'data-error': 'Instrução deve ser preenchida.'})
        }


class InstructionForm(ModelForm):
    class Meta:
        model = Instruction
        fields = ['text']

        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'required': "", 'rows': '6',
                                    'data-error': 'Instrução deve ser preenchida.'}),
        }


class StimulusForm(ModelForm):
    class Meta:
        model = Stimulus
        fields = ['stimulus_type']

        widgets = {
            'stimulus_type': Select(attrs={'class': 'form-control', 'required': "",
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


class BlockForm(ModelForm):
    type = TypedChoiceField(required=True,
                            empty_value=None,
                            choices=(('sequence', 'Sequência'),
                                     ('parallel_block', 'Bloco paralelo')),
                            widget=RadioSelect(attrs={'id': 'id_type', 'required': "",
                                                      'data-error': 'Tipo deve ser escolhido.'}))

    class Meta:
        model = Block
        fields = ['number_of_mandatory_components', 'type']

        widgets = {
            'number_of_mandatory_components': TextInput(attrs={'class': 'form-control', 'required': "",
                                                               'data-error': 'Quantidade deve ser preenchida.'}),
        }


class ResearchProjectForm(ModelForm):
    class Meta:
        model = ResearchProject
        fields = ['start_date', 'end_date', 'title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'required': "",
                                      'data-error': 'Título deve ser preenchido.'}),
            # Even though maxlength is already set in the model, it has be be repeated here, because the form dos not
            # respect that information.
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': "",
                                           'maxlength': '1500',
                                           'data-error': 'Descrição deve ser preenchida.'}),
            'start_date': DateInput(attrs={'class': 'form-control datepicker', 'placeholder': 'dd/mm/aaaa',
                                           'required': "", 'data-error': "Data de início deve ser preenchida"},),
            'end_date': DateInput(attrs={'class': 'form-control datepicker', 'placeholder': 'dd/mm/aaaa'}),

        }

    def clean(self):
        cleaned_data = super(ResearchProjectForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if end_date and end_date < start_date:
            msg = u"Data de início deve ser menor que data de fim."
            self._errors["start_date"] = self.error_class([msg])
            self._errors["end_date"] = self.error_class([msg])

            del cleaned_data["end_date"]
            del cleaned_data["start_date"]

        return cleaned_data
