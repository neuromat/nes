# coding=utf-8

from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, TypedChoiceField, RadioSelect,\
    ValidationError, Form, IntegerField, NumberInput, CharField
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from experiment.models import Experiment, QuestionnaireResponse, SubjectOfGroup, Group, \
    Component, Stimulus, Block, Instruction, ComponentConfiguration, ResearchProject, EEGData, \
    EEGSetting, Equipment, EEG, EEGMachine, EEGMachineSetting, Amplifier, EEGAmplifierSetting, \
    EEGSolution, EEGFilterSetting, FilterType, EEGElectrodeLocalizationSystem, \
    EEGCapSize, EEGElectrodeCap, EEGElectrodePosition, Manufacturer, ElectrodeModel, EEGElectrodeNet, Material, \
    AdditionalData, EMGData, FileFormat, EMGSetting, EMGDigitalFilterSetting


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['research_project', 'title', 'description']

        widgets = {
            'research_project': Select(attrs={'class': 'form-control'}),
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
    # queryset.
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
    # queryset.
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


class EEGForm(ModelForm):

    class Meta:
        model = EEG
        fields = ['eeg_setting']

        widgets = {
            'eeg_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('EEG setting type must be filled.')})
        }

    def __init__(self, *args, **kwargs):
        super(EEGForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            self.fields['eeg_setting'].queryset = EEGSetting.objects.filter(experiment=initial['experiment'])


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
    number_of_uses_to_insert = \
        IntegerField(label='Number of uses to insert', min_value=1, initial=1,
                     widget=NumberInput(attrs={'class': 'form-control',
                                               'required': "",
                                               'data-error': _('Quantity must be filled.')}))


class EEGDataForm(ModelForm):
    class Meta:
        model = EEGData

        fields = ['date', 'file_format', 'eeg_setting', 'eeg_cap_size', 'description', 'file',
                  'file_format_description', 'eeg_setting_reason_for_change']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'eeg_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('EEG setting type must be filled.')}),
            'eeg_cap_size': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Cap size type must be filled.')}),
            'file_format': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('File format must be chosen.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'file_format_description': Textarea(attrs={'class': 'form-control',
                                                       'rows': '4', 'required': "",
                                                       'data-error': _('File format description must be filled.')}),
            'eeg_setting_reason_for_change':
                Textarea(attrs={'class': 'form-control', 'rows': '4',
                                'required': "",
                                'data-error': _('Reason for change must be filled.')}),

            # It is not possible to set the 'required' attribute because it affects the edit screen
            # 'file': FileInput(attrs={'required': ""})
        }

    def __init__(self, *args, **kwargs):
        super(EEGDataForm, self).__init__(*args, **kwargs)

        self.fields['file_format'].queryset = FileFormat.objects.filter(tags__name="EEG")

        initial = kwargs.get('initial')
        if initial and 'experiment' in initial:
            self.fields['eeg_setting'].queryset = EEGSetting.objects.filter(experiment=initial['experiment'])
        if initial and 'eeg_setting' in initial:
            eeg_setting = get_object_or_404(EEGSetting, pk=initial['eeg_setting'])
            self.fields['eeg_cap_size'].queryset = EEGCapSize.objects.filter(id=0)
            if hasattr(eeg_setting, 'eeg_electrode_layout_setting'):
                eeg_electrode_net_id = \
                    eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net.id
                # if the electrode net is a cap
                if EEGElectrodeCap.objects.filter(id=eeg_electrode_net_id):
                    self.fields['eeg_cap_size'].queryset = \
                        EEGCapSize.objects.filter(eeg_electrode_cap_id=eeg_electrode_net_id)


class EEGSettingForm(ModelForm):
    class Meta:
        model = EEGSetting

        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.'),
                                     'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')})
        }


class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        fields = ['description']

        widgets = {
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'disabled': ''})
        }


class EEGMachineForm(ModelForm):
    class Meta:
        model = EEGMachine
        fields = ['number_of_channels', 'software_version']

        widgets = {
            'number_of_channels': TextInput(attrs={'class': 'form-control', 'disabled': ''}),
            'software_version': TextInput(attrs={'class': 'form-control', 'disabled': ''})
        }


class EEGMachineSettingForm(ModelForm):
    class Meta:
        model = EEGMachineSetting
        fields = ['number_of_channels_used']

        widgets = {
            'number_of_channels_used':
                NumberInput(attrs={
                    'class': 'form-control',
                    'required': "",
                    "min": "0",
                    'data-error':
                    _('Number of channels should be between 0 and the number of channels of the EEG machine.')})
        }


class EEGAmplifierForm(ModelForm):
    class Meta:
        model = Amplifier
        fields = ['gain']

        widgets = {
            'gain': TextInput(attrs={'class': 'form-control', 'disabled': ''})
        }


class EEGAmplifierSettingForm(ModelForm):
    class Meta:
        model = EEGAmplifierSetting
        fields = ['gain']

        widgets = {
            'gain': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Description must be filled.')})
        }


class EEGSolutionForm(ModelForm):
    class Meta:
        model = EEGSolution
        fields = ['components']

        widgets = {
            'components': Textarea(attrs={'id': 'id_description', 'class': 'form-control', 'rows': '4', 'disabled': ''})
        }


class EEGFilterForm(ModelForm):
    class Meta:
        model = FilterType
        fields = ['description']

        widgets = {
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'disabled': ''})
        }


class EEGFilterSettingForm(ModelForm):
    class Meta:
        model = EEGFilterSetting
        fields = ['high_pass', 'low_pass', 'order']

        widgets = {
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'order': TextInput(attrs={'class': 'form-control'})
        }


class EEGElectrodeLocalizationSystemRegisterForm(ModelForm):
    class Meta:
        model = EEGElectrodeLocalizationSystem
        fields = ['name', 'description', 'map_image_file']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': "",
                                     'data-error': _('Name field must be filled.'),
                                     'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        }


class EEGElectrodePositionForm(ModelForm):
    class Meta:
        model = EEGElectrodePosition

        fields = ['name', 'coordinate_x', 'coordinate_y', 'position_reference']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': "",
                                     'data-error': _('Name field must be filled.'),
                                     'autofocus': ''}),
            'coordinate_x': TextInput(attrs={'class': 'form-control'}),
            'coordinate_y': TextInput(attrs={'class': 'form-control'}),
            'position_reference': Select(attrs={'class': 'form-control'}),
        }


class ManufacturerRegisterForm(ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')})
        }


class EEGMachineRegisterForm(ModelForm):
    class Meta:
        model = EEGMachine
        fields = ['manufacturer', 'identification', 'description', 'serial_number',
                  'number_of_channels', 'software_version']

        widgets = {

            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),
            'number_of_channels': TextInput(attrs={'class': 'form-control'}),
            'software_version': TextInput(attrs={'class': 'form-control'})
        }


class EEGAmplifierRegisterForm(ModelForm):
    class Meta:
        model = Amplifier
        fields = ['manufacturer', 'identification', 'description', 'serial_number', 'gain']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),
            'gain': TextInput(attrs={'class': 'form-control'})
        }


class EEGSolutionRegisterForm(ModelForm):
    class Meta:
        model = EEGSolution
        fields = ['name', 'components', 'manufacturer']

        widgets = {

            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'components': Textarea(attrs={'id': 'id_description', 'class': 'form-control', 'rows': '4'}),

            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),

        }


class EEGFilterTypeRegisterForm(ModelForm):
    class Meta:
        model = FilterType
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class EEGElectrodeModelRegisterForm(ModelForm):
    class Meta:
        model = ElectrodeModel
        fields = ['name', 'description', 'material', 'usability', 'impedance', 'impedance_unit']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'material': Select(attrs={'class': 'form-control'}),
            'usability': Select(attrs={'class': 'form-control'}),
            'impedance': NumberInput(attrs={'class': 'form-control'}),
            'impedance_unit': Select(attrs={'class': 'form-control'}),
        }


class MaterialRegisterForm(ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class EEGElectrodeNETRegisterForm(ModelForm):
    class Meta:
        model = EEGElectrodeNet
        fields = ['manufacturer', 'identification', 'description', 'serial_number', 'electrode_model_default']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),
            'electrode_model_default': Select(attrs={'class': 'form-control', 'required': "",
                                                     'data-error': _('Electrode model default must be filled in.')}),
        }


class EEGElectrodeCapRegisterForm(ModelForm):
    class Meta:
        model = EEGElectrodeCap
        fields = ['material']
        widgets = {
            'material': Select(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': _('Material must be filled.')})
        }


class EEGCapSizeRegisterForm(ModelForm):
    class Meta:
        model = EEGCapSize
        fields = ['size', 'electrode_adjacent_distance']

        widgets = {
            'size': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Size must be filled.')}),
            'electrode_adjacent_distance':
                NumberInput(attrs={'class': 'form-control',
                                   'data-error': _('Electrode adjacent distance must be filled.')}),
        }


class EMGDataForm(ModelForm):
    class Meta:
        model = EMGData

        fields = ['date', 'file_format', 'description', 'file', 'file_format_description']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'file_format': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('File format must be chosen.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'file_format_description': Textarea(attrs={'class': 'form-control',
                                                       'rows': '4', 'required': "",
                                                       'data-error': _('File format description must be filled.')}),
            # It is not possible to set the 'required' attribute because it affects the edit screen
            # 'file': FileInput(attrs={'required': ""})
        }

    def __init__(self, *args, **kwargs):
        super(EMGDataForm, self).__init__(*args, **kwargs)

        self.fields['file_format'].queryset = FileFormat.objects.filter(tags__name="EMG")


class AdditionalDataForm(ModelForm):
    class Meta:
        model = AdditionalData

        fields = ['date', 'file_format', 'description', 'file', 'file_format_description']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'file_format': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('File format must be chosen.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'file_format_description': Textarea(attrs={'class': 'form-control',
                                                       'rows': '4', 'required': "",
                                                       'data-error': _('File format description must be filled.')}),
            # It is not possible to set the 'required' attribute because it affects the edit screen
            # 'file': FileInput(attrs={'required': ""})
        }


class EMGSettingForm(ModelForm):
    class Meta:
        model = EMGSetting

        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.'),
                                     'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')})
        }


class EMGDigitalFilterSettingForm(ModelForm):
    class Meta:
        model = EMGDigitalFilterSetting

        fields = ['filter_type', 'low_pass', 'high_pass', 'band_pass', 'notch', 'order']

        widgets = {
            'filter_type': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('Filter type is required')}),
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'band_pass': TextInput(attrs={'class': 'form-control'}),
            'notch': TextInput(attrs={'class': 'form-control'}),
            'order': TextInput(attrs={'class': 'form-control'})
        }
