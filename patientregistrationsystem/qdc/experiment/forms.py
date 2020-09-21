# coding=utf-8

from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, TypedChoiceField, RadioSelect, \
    ValidationError, Form, IntegerField, NumberInput, TimeInput, URLInput, ModelChoiceField
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from experiment.models import Experiment, QuestionnaireResponse, SubjectOfGroup, Group, Component, Stimulus, Block, \
    Instruction, ComponentConfiguration, ResearchProject, EEGData, EEGSetting, Equipment, EEG, EMG, Amplifier, \
    EEGAmplifierSetting, EEGSolution, EEGFilterSetting, FilterType, EEGElectrodeLocalizationSystem, \
    EEGCapSize, EEGElectrodeCap, EEGElectrodePosition, Manufacturer, ElectrodeModel, EEGElectrodeNet, Material, \
    AdditionalData, EMGData, FileFormat, EMGSetting, EMGDigitalFilterSetting, EMGADConverterSetting, \
    EMGElectrodeSetting, EMGElectrodePlacementSetting, EMGPreamplifierSetting, EMGAmplifierSetting, \
    EMGAnalogFilterSetting, EMGSurfacePlacement, ADConverter, StandardizationSystem, Muscle, MuscleSide, \
    MuscleSubdivision, TMS, TMSSetting, TMSDeviceSetting, Software, SoftwareVersion, CoilModel, TMSDevice, \
    EMGIntramuscularPlacement, EMGNeedlePlacement, SubjectStepData, EMGPreamplifierFilterSetting, TMSData, HotSpot, \
    CoilOrientation, DirectionOfTheInducedCurrent, TMSLocalizationSystem, DigitalGamePhase, ContextTree, \
    DigitalGamePhaseData, Publication, GenericDataCollection, GenericDataCollectionData, ScheduleOfSending


class ExperimentForm(ModelForm):
    class Meta:
        model = Experiment

        fields = ['research_project', 'title', 'description', 'is_public', 'data_acquisition_is_concluded',
                  'source_code_url', 'ethics_committee_project_url', 'ethics_committee_project_file']

        widgets = {
            'research_project': Select(attrs={'class': 'form-control'}),
            'title': TextInput(attrs={'class': 'form-control',
                                      'required': "",
                                      'data-error': _('Title must be filled.'),
                                      'autofocus': ''}, ),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'source_code_url': URLInput(attrs={'class': 'form-control'}),
            'ethics_committee_project_url': URLInput(attrs={'class': 'form-control'}),
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
                                           'data-error': _('Description must be filled.')}),
        }


class QuestionnaireResponseForm(ModelForm):
    class Meta:
        model = QuestionnaireResponse
        fields = ['date']

        widgets = {
            'date': DateInput(
                format=_("%m/%d/%Y"),
                attrs={'class': 'form-control datepicker',
                       'placeholder': _('mm/dd/yyyy'), 'required': '',
                       'data-error': _('Fill date must be filled.')},
            )
        }


class FileForm(ModelForm):
    class Meta:
        model = SubjectOfGroup
        fields = ['consent_form']


class ComponentForm(ModelForm):
    # TODO Replace "--------" by "Escolha unidade". The old code does not work because ModelChoiceField requires a
    #  queryset.
    #  This is needed because we want an empty_label different from "--------".
    #  duration_unit = ModelChoiceField(
    #      required=False,
    #      empty_label="Escolha unidade",
    #      widget=Select(attrs={'class': 'form-control'}))

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
    #  queryset.
    # This is needed because we want an empty_label different from "--------".
    # interval_between_repetitions_unit = ModelChoiceField(
    #     required=False,
    #     empty_label="Escolha unidade",
    #     widget=Select(attrs={'class': 'form-control', 'required': "",
    #                          'data-error': "Unidade do intervalo deve ser preenchida"}))

    class Meta:
        model = ComponentConfiguration
        fields = ['name', 'random_position', 'number_of_repetitions', 'interval_between_repetitions_value',
                  'interval_between_repetitions_unit', 'requires_start_and_end_datetime']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'number_of_repetitions': TextInput(attrs={'class': 'form-control',
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
        fields = ['stimulus_type', 'media_file']

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


class EMGForm(ModelForm):
    class Meta:
        model = EMG
        fields = ['emg_setting']

        widgets = {
            'emg_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('EMG setting type must be filled.')})
        }

    def __init__(self, *args, **kwargs):
        super(EMGForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            self.fields['emg_setting'].queryset = EMGSetting.objects.filter(experiment=initial['experiment'])


class TMSForm(ModelForm):
    class Meta:
        model = TMS
        fields = ['tms_setting']

        widgets = {
            'tms_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('TMS setting type must be filled.')})
        }

    def __init__(self, *args, **kwargs):
        super(TMSForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            self.fields['tms_setting'].queryset = TMSSetting.objects.filter(experiment=initial['experiment'])


class DigitalGamePhaseForm(ModelForm):
    class Meta:
        model = DigitalGamePhase
        fields = ['software_version', 'context_tree']

        widgets = {
            'software_version': Select(attrs={'class': 'form-control', 'required': "",
                                              'data-error': _('Software version must be filled.')}),
            'context_tree': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Context tree must be filled.')})
        }

    def __init__(self, *args, **kwargs):
        super(DigitalGamePhaseForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        if initial:
            self.fields['context_tree'].queryset = \
                ContextTree.objects.filter(experiment=initial['experiment'])


class GenericDataCollectionForm(ModelForm):
    class Meta:
        model = GenericDataCollection
        fields = ['information_type']

        widgets = {
            'information_type': Select(attrs={'class': 'form-control', 'required': "",
                                              'data-error': _('Information type must be filled.')}),
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


class UserFullnameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return smart_text(obj.get_full_name())


class ResearchProjectOwnerForm(ModelForm):
    owner = UserFullnameChoiceField(queryset=User.objects.all(),
                                    widget=Select(attrs={'class': 'form-control', 'required': ""}))

    class Meta:
        model = ResearchProject
        fields = ['owner']


class ResearchProjectForm(ModelForm):
    class Meta:
        model = ResearchProject
        fields = ['start_date', 'end_date', 'title', 'description']

        widgets = {
            'title': TextInput(
                attrs={'class': 'form-control', 'required': "",
                       'data-error': _('Title must be filled.'),
                       'autofocus': ''}
            ),
            # Even though maxlength is already set in the model, it has be
            # repeated here, because the form dos not respect that information.
            'description': Textarea(
                attrs={
                    'id': 'id_description',
                    'class': 'form-control', 'rows': '4', 'required': "",
                    'data-error': _('Description must be filled.')
                }),
            'start_date': DateInput(
                format=_("%m/%d/%Y"),
                attrs={
                    'id': 'id_start_date', 'class': 'form-control datepicker',
                    'placeholder': _('mm/dd/yyyy'),
                    'required': "",
                    'data-error': _("Initial date must be filled.")
                }, ),
            'end_date': DateInput(
                format=_("%m/%d/%Y"),
                attrs={
                    'id': 'id_end_date', 'class': 'form-control datepicker',
                    'placeholder': _('mm/dd/yyyy')
                }),
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


class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'citation', 'url']

        widgets = {
            'title': Textarea(attrs={'class': 'form-control', 'required': "", 'rows': '2',
                                     'data-error': _('Title must be filled.'),
                                     'autofocus': ''}),
            'citation': Textarea(attrs={'class': 'form-control', 'required': "", 'rows': '6',
                                        'data-error': _('Citation must be filled.')}),
            'url': URLInput(attrs={'class': 'form-control'}),
        }


class NumberOfUsesToInsertForm(Form):
    number_of_uses_to_insert = \
        IntegerField(label='Number of uses to insert', min_value=1, initial=1,
                     widget=NumberInput(attrs={'class': 'form-control',
                                               'required': "",
                                               'data-error': _('Quantity must be filled.')}))


class EEGDataForm(ModelForm):
    class Meta:
        model = EEGData

        fields = ['date', 'time', 'file_format', 'eeg_setting', 'eeg_cap_size', 'description',
                  # 'file',
                  'file_format_description', 'eeg_setting_reason_for_change']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
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


class EEGAmplifierForm(ModelForm):
    class Meta:
        model = Amplifier
        localized_fields = ('gain', 'number_of_channels')
        fields = ['gain', 'number_of_channels']

        widgets = {
            'gain': TextInput(attrs={'class': 'form-control', 'disabled': ''}),
            'number_of_channels': TextInput(attrs={'class': 'form-control', 'disabled': ''}),
        }


class EEGAmplifierSettingForm(ModelForm):
    class Meta:
        model = EEGAmplifierSetting
        localized_fields = ('gain', 'sampling_rate', 'number_of_channels_used')
        fields = ['gain', 'sampling_rate', 'number_of_channels_used']

        widgets = {
            'gain': TextInput(attrs={'class': 'form-control'}),
            'sampling_rate': TextInput(attrs={'class': 'form-control'}),
            'number_of_channels_used':
                NumberInput(attrs={
                    'class': 'form-control',
                    'required': "",
                    "min": "0",
                    'data-error':
                        _('Number of channels should be between 0 and the number of channels of the EEG machine.')}),

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
        localized_fields = ('high_pass', 'low_pass', 'low_band_pass', 'high_band_pass', 'low_notch', 'high_notch')
        fields = ['high_pass', 'low_pass', 'low_band_pass', 'high_band_pass', 'low_notch', 'high_notch', 'order']

        widgets = {
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'low_band_pass': TextInput(attrs={'class': 'form-control'}),
            'high_band_pass': TextInput(attrs={'class': 'form-control'}),
            'low_notch': TextInput(attrs={'class': 'form-control'}),
            'high_notch': TextInput(attrs={'class': 'form-control'}),
            'order': NumberInput(attrs={'class': 'form-control'})
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


class TMSLocalizationSystemForm(ModelForm):
    class Meta:
        model = TMSLocalizationSystem
        fields = ['name', 'description', 'tms_localization_system_image', 'brain_area']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': "",
                                     'data-error': _('Name field must be filled.'),
                                     'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'brain_area': Select(attrs={'class': 'form-control', 'required': ""}),
        }


class EEGElectrodePositionForm(ModelForm):
    class Meta:
        model = EEGElectrodePosition

        fields = ['name', 'coordinate_x', 'coordinate_y', 'position_reference']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': "",
                                     'data-error': _('Name field must be filled.'),
                                     'autofocus': ''}),
            'coordinate_x': NumberInput(attrs={'class': 'form-control'}),
            'coordinate_y': NumberInput(attrs={'class': 'form-control'}),
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


class AmplifierRegisterForm(ModelForm):
    class Meta:
        model = Amplifier

        localized_fields = ('gain', 'common_mode_rejection_ratio', 'input_impedance')

        fields = ['manufacturer', 'identification', 'description', 'serial_number', 'gain', 'number_of_channels',
                  'common_mode_rejection_ratio', 'input_impedance', 'input_impedance_unit', 'amplifier_detection_type',
                  'tethering_system']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),
            'gain': TextInput(attrs={'class': 'form-control'}),
            'number_of_channels': NumberInput(attrs={'class': 'form-control'}),
            'common_mode_rejection_ratio': TextInput(attrs={'class': 'form-control'}),
            'input_impedance': TextInput(attrs={'class': 'form-control'}),
            'input_impedance_unit': Select(attrs={'class': 'form-control'}),
            'tethering_system': Select(attrs={'class': 'form-control'}),
            'amplifier_detection_type': Select(attrs={'class': 'form-control'})
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


class FilterTypeRegisterForm(ModelForm):
    class Meta:
        model = FilterType
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class ElectrodeModelRegisterForm(ModelForm):
    class Meta:
        model = ElectrodeModel
        localized_fields = ('impedance',)
        fields = ['name', 'description', 'material', 'usability', 'impedance', 'impedance_unit', 'electrode_type']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'material': Select(attrs={'class': 'form-control'}),
            'usability': Select(attrs={'class': 'form-control'}),
            'impedance': TextInput(attrs={'class': 'form-control'}),
            'impedance_unit': Select(attrs={'class': 'form-control'}),
            'electrode_type': Select(attrs={'class': 'form-control', 'required': "",
                                            'data-error': _('Electrode type is required')}),
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


class CoilModelRegisterForm(ModelForm):
    class Meta:
        model = CoilModel
        fields = ['name', 'description', 'material', 'coil_shape', 'coil_design']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'material': Select(attrs={'class': 'form-control'}),
            'coil_shape': Select(attrs={'class': 'form-control', 'required': "",
                                        'data-error': _('Coil shape must be filled.')}),
            'coil_design': Select(attrs={'class': 'form-control'})
        }


class TMSDeviceRegisterForm(ModelForm):
    class Meta:
        model = TMSDevice
        # fields = ['manufacturer', 'identification', 'description', 'coil_model', 'pulse_type']
        fields = ['manufacturer', 'identification', 'description', 'pulse_type', 'serial_number']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            # 'coil_model': Select(attrs={'class': 'form-control', 'required': "",
            #                             'data-error': _('Coil model must be filled.')}),
            'pulse_type': Select(attrs={'class': 'form-control'}),
            'serial_number': TextInput(attrs={'class': 'form-control'})
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

    def __init__(self, *args, **kwargs):
        super(EEGElectrodeNETRegisterForm, self).__init__(*args, **kwargs)

        self.fields['electrode_model_default'].queryset = ElectrodeModel.objects.filter(tags__name="EEG")


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
        localized_fields = ('electrode_adjacent_distance',)
        fields = ['size', 'electrode_adjacent_distance']

        widgets = {
            'size': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Size must be filled.')}),
            'electrode_adjacent_distance':
                TextInput(attrs={'class': 'form-control',
                                 'data-error': _('Electrode adjacent distance must be filled.')}),
        }


class ADConverterRegisterForm(ModelForm):
    class Meta:
        model = ADConverter
        localized_fields = ('signal_to_noise_rate', 'sampling_rate', 'resolution')
        fields = ['manufacturer', 'identification', 'description', 'serial_number',
                  'signal_to_noise_rate', 'sampling_rate', 'resolution']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'identification': TextInput(attrs={'class': 'form-control', 'required': "",
                                               'data-error': _('Identification must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),

            'signal_to_noise_rate': TextInput(attrs={'class': 'form-control'}),
            'sampling_rate': TextInput(attrs={'class': 'form-control'}),
            'resolution': TextInput(attrs={'class': 'form-control'})
        }


class StandardizationSystemRegisterForm(ModelForm):
    class Meta:
        model = StandardizationSystem
        fields = ['name', 'description']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),

            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class EMGSurfacePlacementRegisterForm(ModelForm):
    class Meta:
        model = EMGSurfacePlacement

        fields = ['muscle_subdivision', 'location', 'start_posture', 'orientation', 'fixation_on_the_skin',
                  'reference_electrode', 'clinical_test', 'photo']

        widgets = {
            'muscle_subdivision': Select(attrs={'class': 'form-control', 'required': "",
                                                'data-error': _('Muscle subdivision is required.')}),
            'location': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'start_posture': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'orientation': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'fixation_on_the_skin': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'reference_electrode': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'clinical_test': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        }


class EMGIntramuscularPlacementRegisterForm(ModelForm):
    class Meta:
        model = EMGIntramuscularPlacement

        fields = ['muscle_subdivision', 'location', 'method_of_insertion', 'depth_of_insertion', 'photo']

        widgets = {
            'muscle_subdivision': Select(attrs={'class': 'form-control', 'required': "",
                                                'data-error': _('Muscle subdivision is required.')}),
            'location': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'method_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'depth_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        }


class EMGNeedlePlacementRegisterForm(ModelForm):
    class Meta:
        model = EMGNeedlePlacement

        fields = ['muscle_subdivision', 'location', 'depth_of_insertion', 'photo']

        widgets = {
            'muscle_subdivision': Select(attrs={'class': 'form-control', 'required': "",
                                                'data-error': _('Muscle subdivision is required.')}),
            'location': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'depth_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
        }


class MuscleRegisterForm(ModelForm):
    class Meta:
        model = Muscle
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
        }


class MuscleSubdivisionRegisterForm(ModelForm):
    class Meta:
        model = MuscleSubdivision
        fields = ['name', 'anatomy_origin', 'anatomy_insertion', 'anatomy_function']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
            'anatomy_origin': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'anatomy_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'anatomy_function': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class MuscleSideRegisterForm(ModelForm):
    class Meta:
        model = MuscleSide
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
        }


class SoftwareRegisterForm(ModelForm):
    class Meta:
        model = Software
        fields = ['manufacturer', 'name', 'description']

        widgets = {
            'manufacturer': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('Manufacturer must be filled.')}),
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4'})
        }


class SoftwareVersionRegisterForm(ModelForm):
    class Meta:
        model = SoftwareVersion
        fields = ['name']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
        }


class EMGDataForm(ModelForm):
    class Meta:
        model = EMGData

        fields = ['date', 'time', 'file_format', 'emg_setting', 'description',
                  # 'file',
                  'file_format_description', 'emg_setting_reason_for_change']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
            'emg_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('EMG setting type must be filled.')}),
            'file_format': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('File format must be chosen.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'file_format_description': Textarea(attrs={'class': 'form-control',
                                                       'rows': '4', 'required': "",
                                                       'data-error': _('File format description must be filled.')}),
            'emg_setting_reason_for_change':
                Textarea(attrs={'class': 'form-control', 'rows': '4',
                                'required': "",
                                'data-error': _('Reason for change must be filled.')}),
            # It is not possible to set the 'required' attribute because it affects the edit screen
            # 'file': FileInput(attrs={'required': ""})
        }

    def __init__(self, *args, **kwargs):
        super(EMGDataForm, self).__init__(*args, **kwargs)

        # emg_setting has no blank option
        self.fields['emg_setting'].empty_label = None
        self.fields['file_format'].queryset = FileFormat.objects.filter(tags__name="EMG")
        initial = kwargs.get('initial')
        if initial and 'experiment' in initial:
            self.fields['emg_setting'].queryset = EMGSetting.objects.filter(experiment=initial['experiment'])
        if initial and 'emg_setting' in initial:
            emg_setting = get_object_or_404(EMGSetting, pk=initial['emg_setting'])


class AdditionalDataForm(ModelForm):
    class Meta:
        model = AdditionalData

        fields = ['date', 'file_format', 'description',
                  # 'file',
                  'file_format_description']

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


class SubjectStepDataForm(ModelForm):
    class Meta:
        model = SubjectStepData

        fields = ['start_date', 'start_time', 'end_date', 'end_time']

        widgets = {
            'start_date': DateInput(format=_("%m/%d/%Y"),
                                    attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                           'required': "", 'data-error': _("Start date must be filled.")}, ),
            'start_time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
            'end_date': DateInput(format=_("%m/%d/%Y"),
                                  attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                         'required': "", 'data-error': _("End date must be filled.")}, ),
            'end_time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
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
        localized_fields = ('low_pass', 'high_pass', 'low_band_pass', 'high_band_pass', 'low_notch',
                            'high_notch', 'order')
        fields = ['filter_type', 'low_pass', 'high_pass', 'low_band_pass', 'high_band_pass', 'low_notch',
                  'high_notch', 'order']

        widgets = {
            'filter_type': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('Filter type is required')}),
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'low_band_pass': TextInput(attrs={'class': 'form-control'}),
            'low_notch': TextInput(attrs={'class': 'form-control'}),
            'high_band_pass': TextInput(attrs={'class': 'form-control'}),
            'high_notch': TextInput(attrs={'class': 'form-control'}),
            'order': NumberInput(attrs={'class': 'form-control'})
        }


class EMGADConverterSettingForm(ModelForm):
    class Meta:
        model = EMGADConverterSetting
        localized_fields = ('sampling_rate',)
        fields = ['ad_converter', 'sampling_rate']

        widgets = {
            'ad_converter': Select(attrs={'class': 'form-control', 'required': "",
                                          'data-error': _('AD converter is required')}),
            'sampling_rate': TextInput(attrs={'class': 'form-control'})
        }


class EMGElectrodeSettingForm(ModelForm):
    class Meta:
        model = EMGElectrodeSetting

        fields = ['electrode']

        widgets = {
            'electrode': Select(attrs={'class': 'form-control', 'required': "",
                                       'data-error': _('Electrode is required')})
        }

    def __init__(self, *args, **kwargs):
        super(EMGElectrodeSettingForm, self).__init__(*args, **kwargs)

        self.fields['electrode'].queryset = ElectrodeModel.objects.filter(tags__name="EMG")


class EMGElectrodePlacementSettingForm(ModelForm):
    class Meta:
        model = EMGElectrodePlacementSetting

        fields = ['emg_electrode_placement', 'remarks', 'muscle_side']

        widgets = {
            'emg_electrode_placement': Select(attrs={'class': 'form-control', 'required': "",
                                                     'data-error': _('Electrode placement is required')}),
            'remarks': Textarea(attrs={'class': 'form-control', 'rows': '4'}),
            'muscle_side': Select(attrs={'class': 'form-control',
                                         'required': "", 'data-error': _('Muscle side is required')})
        }


class EMGPreamplifierSettingForm(ModelForm):
    class Meta:
        model = EMGPreamplifierSetting
        localized_fields = ('gain',)
        fields = ['amplifier', 'gain']

        widgets = {
            'amplifier': Select(attrs={'class': 'form-control', 'required': "",
                                       'data-error': _('Amplifier is required')}),
            'gain': TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(EMGPreamplifierSettingForm, self).__init__(*args, **kwargs)

        self.fields['amplifier'].queryset = Amplifier.objects.filter(tags__name="EMG")


class EMGPreamplifierFilterSettingForm(ModelForm):
    class Meta:
        model = EMGPreamplifierFilterSetting

        localized_fields = ('low_pass', 'high_pass', 'low_band_pass', 'low_notch', 'high_band_pass', 'high_notch')
        fields = ['low_pass', 'high_pass', 'low_band_pass', 'low_notch', 'high_band_pass', 'high_notch', 'order']

        widgets = {
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'low_band_pass': TextInput(attrs={'class': 'form-control'}),
            'low_notch': TextInput(attrs={'class': 'form-control'}),
            'high_band_pass': TextInput(attrs={'class': 'form-control'}),
            'high_notch': TextInput(attrs={'class': 'form-control'}),
            'order': NumberInput(attrs={'class': 'form-control'})
        }


class EMGAmplifierSettingForm(ModelForm):
    class Meta:
        model = EMGAmplifierSetting

        localized_fields = ('gain',)
        fields = ['amplifier', 'gain']

        widgets = {
            'amplifier': Select(attrs={'class': 'form-control', 'required': "",
                                       'data-error': _('Amplifier is required')}),
            'gain': TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(EMGAmplifierSettingForm, self).__init__(*args, **kwargs)

        self.fields['amplifier'].queryset = Amplifier.objects.filter(tags__name="EMG")


class EMGAnalogFilterSettingForm(ModelForm):
    class Meta:
        model = EMGAnalogFilterSetting

        localized_fields = ('low_pass', 'high_pass', 'low_band_pass', 'low_notch', 'high_band_pass', 'high_notch')
        fields = ['low_pass', 'high_pass', 'low_band_pass', 'low_notch', 'high_band_pass', 'high_notch', 'order']

        widgets = {
            'low_pass': TextInput(attrs={'class': 'form-control'}),
            'high_pass': TextInput(attrs={'class': 'form-control'}),
            'low_band_pass': TextInput(attrs={'class': 'form-control'}),
            'low_notch': TextInput(attrs={'class': 'form-control'}),
            'high_band_pass': TextInput(attrs={'class': 'form-control'}),
            'high_notch': TextInput(attrs={'class': 'form-control'}),
            'order': NumberInput(attrs={'class': 'form-control'})
        }


class ElectrodeModelForm(ModelForm):
    class Meta:
        model = ElectrodeModel

        fields = ['name', 'description', 'electrode_type']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'electrode_type': Select(attrs={'class': 'form-control', 'required': "",
                                            'data-error': _('Electrode type is required')}),
        }


class EMGSurfacePlacementForm(ModelForm):
    class Meta:
        model = EMGSurfacePlacement

        fields = ['start_posture', 'orientation', 'fixation_on_the_skin', 'reference_electrode', 'clinical_test']

        widgets = {
            'start_posture': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
            'orientation': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
            'fixation_on_the_skin': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
            'reference_electrode': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
            'clinical_test': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
        }


class EMGIntramuscularPlacementForm(ModelForm):
    class Meta:
        model = EMGIntramuscularPlacement

        fields = ['method_of_insertion', 'depth_of_insertion']

        widgets = {
            'method_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""}),
            'depth_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""})
        }


class EMGNeedlePlacementForm(ModelForm):
    class Meta:
        model = EMGNeedlePlacement

        fields = ['depth_of_insertion']

        widgets = {
            'depth_of_insertion': Textarea(attrs={'class': 'form-control', 'rows': '4', 'required': ""})
        }


class TMSDataForm(ModelForm):
    class Meta:
        model = TMSData

        fields = ['date', 'time', 'tms_setting', 'coil_orientation', 'direction_of_induced_current',
                  'resting_motor_threshold', 'test_pulse_intensity_of_simulation', 'interval_between_pulses',
                  'interval_between_pulses_unit', 'time_between_mep_trials', 'time_between_mep_trials_unit',
                  'coil_orientation_angle', 'repetitive_pulse_frequency', 'description', 'second_test_pulse_intensity']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
            'tms_setting': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('TMS setting type must be filled.')}),
            'coil_orientation': Select(attrs={'class': 'form-control'}),
            'coil_orientation_angle': TextInput(attrs={'class': 'form-control'}),
            'direction_of_induced_current': Select(attrs={'class': 'form-control'}),
            'resting_motor_threshold': TextInput(attrs={'class': 'form-control'}),
            'test_pulse_intensity_of_simulation': TextInput(attrs={'class': 'form-control'}),
            'second_test_pulse_intensity': TextInput(attrs={'class': 'form-control'}),
            'interval_between_pulses': TextInput(attrs={'class': 'form-control'}),
            'interval_between_pulses_unit': Select(attrs={'class': 'form-control'}),
            'time_between_mep_trials': TextInput(attrs={'class': 'form-control'}),
            'time_between_mep_trials_unit': Select(attrs={'class': 'form-control'}),
            'repetitive_pulse_frequency': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
        }

    def __init__(self, *args, **kwargs):
        super(TMSDataForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial')
        if initial and 'experiment' in initial:
            self.fields['tms_setting'].queryset = TMSSetting.objects.filter(experiment=initial['experiment'])
        if initial and 'tms_setting' in initial:
            tms_setting = get_object_or_404(TMSSetting, pk=initial['tms_setting'])
            self.fields['coil_orientation'].queryset = CoilOrientation.objects.all()
            self.fields['direction_of_induced_current'].queryset = DirectionOfTheInducedCurrent.objects.all()


class HotSpotForm(ModelForm):
    class Meta:
        model = HotSpot

        fields = ['name', 'coordinate_x', 'coordinate_y', 'hot_spot_map']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'coordinate_x': TextInput(attrs={'class': 'form-control',
                                             'required': "",
                                             'data-error': _('The coordinate must be filled.')}),
            'coordinate_y': TextInput(attrs={'class': 'form-control',
                                             'required': "",
                                             'data-error': _('The coordinate must be filled.')}),
        }


class TMSSettingForm(ModelForm):
    class Meta:
        model = TMSSetting

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


class TMSDeviceSettingForm(ModelForm):
    class Meta:
        model = TMSDeviceSetting

        fields = ['tms_device', 'pulse_stimulus_type', 'coil_model']

        widgets = {
            'tms_device': Select(attrs={'class': 'form-control', 'required': "",
                                        'data-error': _('TMS device is required')}),
            'coil_model': Select(attrs={'class': 'form-control', 'required': "",
                                        'data-error': _('Coil model is required')}),
            'pulse_stimulus_type': Select(attrs={'class': 'form-control'})
        }


class CoilModelForm(ModelForm):
    class Meta:
        model = CoilModel

        fields = ['description']

        widgets = {
            'description': Textarea(attrs={'class': 'form-control', 'rows': '4', 'disabled': '',
                                           'id': 'id_coil_description'})
        }


class ContextTreeForm(ModelForm):
    class Meta:
        model = ContextTree

        fields = ['name', 'description', 'setting_text', 'setting_file']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control',
                                     'required': "",
                                     'data-error': _('Name must be filled.'),
                                     'autofocus': ''}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'setting_text': Textarea(attrs={'class': 'form-control', 'rows': '6'})
        }


class DigitalGamePhaseDataForm(ModelForm):
    class Meta:
        model = DigitalGamePhaseData

        fields = ['date', 'time', 'file_format', 'description',
                  # 'file',
                  'file_format_description', 'sequence_used_in_context_tree']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
            'file_format': Select(attrs={'class': 'form-control', 'required': "",
                                         'data-error': _('File format must be chosen.')}),
            'description': Textarea(attrs={'class': 'form-control',
                                           'rows': '4', 'required': "",
                                           'data-error': _('Description must be filled.')}),
            'file_format_description': Textarea(attrs={'class': 'form-control',
                                                       'rows': '4', 'required': "",
                                                       'data-error': _('File format description must be filled.')}),
            'sequence_used_in_context_tree': Textarea(attrs={'class': 'form-control', 'rows': '4'})
            # It is not possible to set the 'required' attribute because it affects the edit screen
            # 'file': FileInput(attrs={'required': ""})
        }

    def __init__(self, *args, **kwargs):
        super(DigitalGamePhaseDataForm, self).__init__(*args, **kwargs)


class GenericDataCollectionDataForm(ModelForm):
    class Meta:
        model = GenericDataCollectionData

        fields = ['date', 'time', 'file_format', 'description',
                  # 'file',
                  'file_format_description']

        widgets = {
            'date': DateInput(format=_("%m/%d/%Y"),
                              attrs={'class': 'form-control datepicker', 'placeholder': _('mm/dd/yyyy'),
                                     'required': "",
                                     'data-error': _("Fill date must be filled.")}, ),
            'time': TimeInput(attrs={'class': 'form-control', 'placeholder': 'HH:mm:ss'}),
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
        super(GenericDataCollectionDataForm, self).__init__(*args, **kwargs)


class ResendExperimentForm(ModelForm):
    class Meta:
        model = ScheduleOfSending

        fields = ['reason_for_resending']

        widgets = {
            'reason_for_resending': Textarea(attrs={'class': 'form-control',
                                                    'rows': '4', 'required': "",
                                                    'data-error': _('Reason must be filled.'),
                                                    'autofocus': ''}),
        }
