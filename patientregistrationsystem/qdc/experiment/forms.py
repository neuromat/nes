# coding=utf-8
from experiment.models import Experiment, QuestionnaireResponse, SubjectOfGroup, Group, \
    Component, Stimulus, Block, Instruction, ComponentConfiguration, ResearchProject
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, TypedChoiceField, RadioSelect,\
    ValidationError, Form, IntegerField, NumberInput, CharField
from django.utils.translation import ugettext_lazy as _


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['research_project', 'title', 'description']

        widgets = {
            'research_project': Select(attrs={'class': 'form-control'}, choices='research_projects'),
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': _('Title must be filled.'),
                                      'autofocus': ''},),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
        }


class GroupForm(ModelForm):
    class Meta:

        model = Group

        fields = ['title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': _('Title must be filled.'),
                                      'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')})
        }


class QuestionnaireResponseForm(ModelForm):
    class Meta:
        model = QuestionnaireResponse
        fields = [
            'date',
        ]

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, )
        }


class FileForm(ModelForm):
    class Meta:
        model = SubjectOfGroup
        fields = ['consent_form']


class ComponentForm(ModelForm):
    # TODO Replace "--------" by "Escolha unidade". The old code does not work because ModelChoiceField requires a
    # TODO queryset.
    # This is needed because we want an empty_label different from "--------".
    # duration_unit = ModelChoiceField(
    #     required=False,
    #     empty_label="Escolha unidade",
    #     widget=Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Component
        fields = ['identification', 'description', 'duration_value', 'duration_unit']

        widgets = {
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.'),
                                               'autofocus': ''}),
            # Even though maxlength is already set in the model, it has be be repeated here, because the form dos not
            # respect that information.
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'duration_value': TextInput(attrs={'class': 'form-control', 'placeholder': _('Time')}),
            'duration_unit': Select(attrs={'class': 'form-control'}),
        }

    def clean_duration_value(self):
        duration_value = self.cleaned_data['duration_value']

        if self.component_type == "pause" and duration_value is None:
            raise ValidationError(_("Duration time must be filled in."))

        return duration_value

    def clean_duration_unit(self):
        duration_unit = self.cleaned_data['duration_unit']

        if self.component_type == "pause" and duration_unit is None:
            raise ValidationError(_("Duration unit must be filled in."))

        return duration_unit


class ComponentConfigurationForm(ModelForm):
    # This is needed because it will be included only when the parent is a sequence.
    random_position = TypedChoiceField(required=False,
                                       empty_value=None,
                                       choices=((False, _('Fixed')), (True, _('Random'))),
                                       widget=RadioSelect(attrs={'id': 'id_random_position'}))

    # TODO Replace "--------" by "Escolha unidade". The old code does not work because ModelChoiceField requires a
    # TODO queryset.
    # This is needed because we want an empty_label different from "--------".
    # interval_between_repetitions_unit = ModelChoiceField(
    #     required=False,
    #     empty_label="Escolha unidade",
    #     widget=Select(attrs={'class': 'form-control', 'required': "",
    #                          'data-error': "Unidade do intervalo deve ser preenchida"}))

    class Meta:
        model = ComponentConfiguration
        fields = ['name', 'random_position', 'number_of_repetitions', 'interval_between_repetitions_value',
                  'interval_between_repetitions_unit']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'number_of_repetitions': TextInput(attrs={'class': 'form-control', 'required': "",
                                                      'data-error': _('Quantity of repetitions must be filled.')}),
            'interval_between_repetitions_value': TextInput(attrs={'class': 'form-control', 'required': "",
                                                                   'data-error': _('Interval must be filled.'),
                                                                   'placeholder': _('Time')}),
            'interval_between_repetitions_unit': Select(
                attrs={'class': 'form-control',
                       'required': "",
                       'data-error': _('Interval unit must be filled.')}),
        }


class InstructionForm(ModelForm):
    class Meta:
        model = Instruction
        fields = ['text']

        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'required': "", 'rows': '6',
                                    'data-error': _('Instruction must be filled.')}),
        }


class StimulusForm(ModelForm):
    class Meta:
        model = Stimulus
        fields = ['stimulus_type']

        widgets = {
            'stimulus_type': Select(attrs={'class': 'form-control', 'required': "",
                                           'data-error': _('Stimulus type must be filled.')})
        }


class BlockForm(ModelForm):
    type = TypedChoiceField(required=True,
                            empty_value=None,
                            choices=(('sequence', _('Sequence')),
                                     ('parallel_block', _('Parallel'))),
                            widget=RadioSelect(attrs={'id': 'id_type', 'required': "",
                                                      'data-error': _('Organization type must be filled in.')}))

    class Meta:
        model = Block
        fields = ['number_of_mandatory_components', 'type']

        widgets = {
            'number_of_mandatory_components': TextInput(attrs={'class': 'form-control', 'required': "",
                                                               'data-error': _('Quantity must be filled.')}),
        }


class ResearchProjectForm(ModelForm):
    owners_full_name = CharField(label=_('Responsible'),
                                 widget=TextInput(attrs={'class': 'form-control', 'disabled': 'True'}),
                                 required=False)

    class Meta:
        model = ResearchProject
        fields = ['start_date', 'end_date', 'title', 'description']

        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'required': "",
                                      'data-error': _('Title must be filled.'),
                                      'autofocus': ''}),
            # Even though maxlength is already set in the model, it has be be repeated here, because the form dos not
            # respect that information.
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'start_date': DateInput(format=_("%m/%d/%Y"),
                                    attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                           'required': "", 'data-error': _("Initial date must be filled.")},),
            'end_date': DateInput(format=_("%m/%d/%Y"),
                                  attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy')}),
        }

    def clean(self):
        cleaned_data = super(ResearchProjectForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if end_date and end_date < start_date:
            msg = "Data de início deve ser menor que data de fim."
            self._errors["start_date"] = self.error_class([msg])
            self._errors["end_date"] = self.error_class([msg])

            del cleaned_data["end_date"]
            del cleaned_data["start_date"]

        return cleaned_data


class NumberOfUsesToInsertForm(Form):
    number_of_uses_to_insert = IntegerField(label='Number of uses to insert', min_value=1, initial=1,
                                            widget=NumberInput(attrs={'class': 'form-control', 'required': "",
                                                                      'data-error': _('Quantity must be filled.')}))
