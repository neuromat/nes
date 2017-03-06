# -*- coding: UTF-8 -*-
import datetime

from os import path

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from patient.models import Patient, ClassificationOfDiseases
from survey.models import Survey
from team.models import TeamPerson


TIME_UNITS = (
    ("ms", _("milisecond(s)")),
    ("s", _("second(s)")),
    ("min", _("minute(s)")),
    ("h", _("hour(s)")),
    ("d", _("day(s)")),
    ("w", _("week(s)")),
    ("mon", _("month(s)")),
    ("y", _("year(s)")),
)

IMPEDANCE_UNIT = (
    ("ohm", _("Ohm(s)")),
    ("kilohm", _("Kilohm(s)")),
    ("megaohm", _("Megaohm(s)")),
    ("gigaohm", _("Gigaohm(s)"))
)


def validate_date_questionnaire_response(value):
    if value > datetime.date.today():
        raise ValidationError(_("Date cannot be greater than today's date."))


class Subject(models.Model):
    patient = models.ForeignKey(Patient)


class StimulusType(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class ResearchProject(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    keywords = models.ManyToManyField(Keyword)
    owner = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("view_researchproject", "Can view research project"),
            ("change_researchproject_from_others", "Can change research project created by others"),
        )


class ResearchProjectCollaboration(models.Model):
    team_person = models.ForeignKey(TeamPerson, related_name='collaborators')
    research_project = models.ForeignKey(ResearchProject, related_name='collaborators')
    is_coordinator = models.BooleanField()


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=150, blank=False)
    description = models.TextField(null=False, blank=False)
    research_project = models.ForeignKey(ResearchProject, null=False, blank=False)
    is_public = models.BooleanField(default=False)
    data_acquisition_is_concluded = models.BooleanField(default=False)

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.title

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class Publication(models.Model):
    title = models.CharField(max_length=255)
    citation = models.TextField()
    url = models.URLField(null=True, blank=True)
    experiments = models.ManyToManyField(Experiment)


class Manufacturer(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    EQUIPMENT_TYPES = (
        ("eeg_machine", _("EEG Machine")),
        ("amplifier", _("Amplifier")),
        ("eeg_solution", _("EEG Solution")),
        ("filter", _("Filter")),
        ("eeg_electrode_net", _("EEG Electrode Net")),
        ("ad_converter", _("A/D Converter")),
        ("tms_device", _("TMS device"))
    )
    manufacturer = models.ForeignKey(Manufacturer, null=False, related_name="set_of_equipment")
    equipment_type = models.CharField(null=True, blank=True, max_length=50, choices=EQUIPMENT_TYPES)
    identification = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.identification

    class Meta:
        verbose_name = _('Equipment')
        verbose_name_plural = _('Equipment')

        permissions = (
            ("register_equipment", "Can register equipment"),
        )


class AmplifierDetectionType(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class TetheringSystem(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Amplifier(Equipment):
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    number_of_channels = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    common_mode_rejection_ratio = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    input_impedance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    input_impedance_unit = models.CharField(null=True, blank=True, max_length=15, choices=IMPEDANCE_UNIT)
    amplifier_detection_type = models.ForeignKey(AmplifierDetectionType, null=True, blank=True)
    tethering_system = models.ForeignKey(TetheringSystem, null=True, blank=True)


class EEGSolution(models.Model):
    name = models.CharField(max_length=150)
    components = models.TextField(null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, null=False, related_name="set_of_solution")


class FilterType(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ElectrodeConfiguration(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class ElectrodeModel(models.Model):
    USABILITY_TYPES = (
        ("disposable", _("Disposable")),
        ("reusable", _("Reusable")),
    )
    ELECTRODE_TYPES = (
        ("surface", _("Surface")),
        ("intramuscular", _("Intramuscular")),
        ("needle", _("Needle")),
    )
    ELECTRODE_DISTANCE_UNIT = (
        ("mm", _("millimeter(s)")),
        ("cm", _("centimeter(s)")),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    material = models.ForeignKey(Material, null=True, blank=True)
    usability = models.CharField(null=True, blank=True, max_length=50, choices=USABILITY_TYPES)
    impedance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    impedance_unit = models.CharField(null=True, blank=True, max_length=15, choices=IMPEDANCE_UNIT)
    tags = models.ManyToManyField(Tag)
    inter_electrode_distance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    inter_electrode_distance_unit = models.CharField(null=True, blank=True, max_length=10,
                                                     choices=ELECTRODE_DISTANCE_UNIT)
    electrode_configuration = models.ForeignKey(ElectrodeConfiguration, null=True, blank=True)
    electrode_type = models.CharField(max_length=50, choices=ELECTRODE_TYPES)

    def __str__(self):
        return self.name


class MeasureSystem(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class MeasureUnit(models.Model):
    name = models.CharField(max_length=150)
    measure_system = models.ForeignKey(MeasureSystem)

    def __str__(self):
        return self.name


class ElectrodeShape(models.Model):
    name = models.CharField(max_length=150)
    measure_systems = models.ManyToManyField(MeasureSystem)

    def __str__(self):
        return self.name


class SurfaceElectrode(ElectrodeModel):
    CONDUCTION_TYPES = (
        ("gelled", _("Gelled")),
        ("dry", _("Dry")),
    )
    MODE_OPTIONS = (
        ("active", _("Active")),
        ("passive", _("Passive")),
    )
    conduction_type = models.CharField(max_length=20, choices=CONDUCTION_TYPES)
    electrode_mode = models.CharField(max_length=20, choices=MODE_OPTIONS)
    electrode_shape = models.ForeignKey(ElectrodeShape)

    def save(self, *args, **kwargs):
        super(ElectrodeModel, self).save(*args, **kwargs)


class ElectrodeSurfaceMeasure(models.Model):
    electrode_surface = models.ForeignKey(SurfaceElectrode)
    measure_unit = models.ForeignKey(MeasureUnit)
    value = models.FloatField(validators=[MinValueValidator(0)])


class IntramuscularElectrode(ElectrodeModel):
    STRAND_TYPES = (
        ("single", _("Single")),
        ("multi", _("Multi")),
    )
    strand = models.CharField(max_length=20, choices=STRAND_TYPES)
    insulation_material = models.ForeignKey(Material, null=True, blank=True)
    length_of_exposed_tip = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        super(ElectrodeModel, self).save(*args, **kwargs)


class NeedleElectrode(ElectrodeModel):
    SIZE_UNIT = (
        ("mm", _("millimeter(s)")),
        ("cm", _("centimeter(s)")),
    )
    size = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    size_unit = models.CharField(max_length=10, choices=SIZE_UNIT)
    number_of_conductive_contact_points_at_the_tip = models.IntegerField(null=True, blank=True,
                                                                         validators=[MinValueValidator(0)])
    size_of_conductive_contact_points_at_the_tip = models.FloatField(null=True, blank=True,
                                                                     validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        super(ElectrodeModel, self).save(*args, **kwargs)


class EEGElectrodeNet(Equipment):
    electrode_model_default = models.ForeignKey(ElectrodeModel)

    def __str__(self):
        return self.identification


class EEGElectrodeCap(EEGElectrodeNet):
    material = models.ForeignKey(Material, null=True, blank=True)


class EEGCapSize(models.Model):
    eeg_electrode_cap = models.ForeignKey(EEGElectrodeCap)
    size = models.CharField(max_length=30)
    electrode_adjacent_distance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.size


def get_eeg_electrode_system_dir(instance, filename):
    return "eeg_electrode_system_files/%s/%s" % \
           (instance.id, filename)


class EEGElectrodeLocalizationSystem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    map_image_file = models.FileField(upload_to=get_eeg_electrode_system_dir, null=True, blank=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.map_image_file.delete()
        super(EEGElectrodeLocalizationSystem, self).delete(*args, **kwargs)


class EEGElectrodePosition(models.Model):
    eeg_electrode_localization_system = models.ForeignKey(EEGElectrodeLocalizationSystem,
                                                          related_name="electrode_positions")
    name = models.CharField(max_length=150)
    coordinate_x = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    coordinate_y = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    position_reference = models.ForeignKey('self', null=True, blank=True, related_name='children')
    channel_default_index = models.IntegerField()

    class Meta:
        unique_together = ('eeg_electrode_localization_system', 'channel_default_index')

    def __str__(self):
        return self.eeg_electrode_localization_system.name + ' - ' + self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and not self.channel_default_index:
            top = \
                EEGElectrodePosition.objects.filter(
                    eeg_electrode_localization_system=self.eeg_electrode_localization_system).order_by(
                    '-channel_default_index').first()
            self.channel_default_index = top.channel_default_index + 1 if top else 1
        super(EEGElectrodePosition, self).save()


class EEGElectrodeNetSystem(models.Model):
    eeg_electrode_net = models.ForeignKey(EEGElectrodeNet, related_name="set_of_electrode_net_system")
    eeg_electrode_localization_system = models.ForeignKey(EEGElectrodeLocalizationSystem,
                                                          related_name='set_of_electrode_net_system')


class CoilShape(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class CoilModel(models.Model):
    COIL_DESIGN_OPTIONS = (
        ("air_core_coil", _("Air core coil")),
        ("solid_core_coil", _("Solid core coil")),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    coil_shape = models.ForeignKey(CoilShape)
    material = models.ForeignKey(Material, null=True, blank=True)
    coil_design = models.CharField(null=True, blank=True, max_length=50, choices=COIL_DESIGN_OPTIONS)

    def __str__(self):
        return self.name


class TMSDevice(Equipment):
    PULSE_TYPES = (
        ("monophase", _("Monophase")),
        ("biphase", _("Biphase")),
    )

    pulse_type = models.CharField(null=True, blank=True, max_length=50, choices=PULSE_TYPES)

    def __str__(self):
        return self.identification


class EEGSetting(models.Model):
    experiment = models.ForeignKey(Experiment)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey('self', null=True, related_name='children')
    # set_of_equipment = models.ManyToManyField(Equipment)

    def __str__(self):
        return self.name


class EEGAmplifierSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_amplifier_setting')
    eeg_amplifier = models.ForeignKey(Amplifier)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    sampling_rate = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    number_of_channels_used = models.IntegerField(null=True, validators=[MinValueValidator(0)])


class EEGSolutionSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_solution_setting')
    eeg_solution = models.ForeignKey(EEGSolution)


class EEGFilterSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_filter_setting')
    eeg_filter_type = models.ForeignKey(FilterType)
    high_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])


class EEGElectrodeLayoutSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_electrode_layout_setting')
    eeg_electrode_net_system = models.ForeignKey(EEGElectrodeNetSystem)


class EEGElectrodePositionSetting(models.Model):
    eeg_electrode_layout_setting = models.ForeignKey(EEGElectrodeLayoutSetting, related_name='positions_setting')
    eeg_electrode_position = models.ForeignKey(EEGElectrodePosition)
    used = models.BooleanField()
    electrode_model = models.ForeignKey(ElectrodeModel)
    channel_index = models.IntegerField()

    class Meta:
        unique_together = ('eeg_electrode_layout_setting', 'channel_index')


class Software(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class SoftwareVersion(models.Model):
    software = models.ForeignKey(Software, related_name='versions')
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.software.name + ' - ' + self.name


class ADConverter(Equipment):
    signal_to_noise_rate = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    sampling_rate = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    resolution = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])


class StandardizationSystem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Muscle(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class MuscleSubdivision(models.Model):
    muscle = models.ForeignKey(Muscle)
    name = models.CharField(max_length=150)
    anatomy_origin = models.TextField(null=True, blank=True)
    anatomy_insertion = models.TextField(null=True, blank=True)
    anatomy_function = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.muscle.name + ' - ' + self.name


class MuscleSide(models.Model):
    muscle = models.ForeignKey(Muscle)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


def get_emg_placement_dir(instance, filename):
    return "emg_placement_files/%s/%s" % \
           (instance.standardization_system.id, filename)


class EMGElectrodePlacement(models.Model):
    PLACEMENT_TYPES = (
        ("surface", _("Surface")),
        ("intramuscular", _("Intramuscular")),
        ("needle", _("Needle")),
    )
    standardization_system = models.ForeignKey(StandardizationSystem, related_name='electrode_placements')
    muscle_subdivision = models.ForeignKey(MuscleSubdivision)
    placement_reference = models.ForeignKey('self', null=True, blank=True, related_name='children')
    photo = models.FileField(upload_to=get_emg_placement_dir, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    placement_type = models.CharField(max_length=50, choices=PLACEMENT_TYPES)

    def __str__(self):
        return self.standardization_system.name + ' - ' + \
               self.muscle_subdivision.muscle.name + ' - ' + self.muscle_subdivision.name

    def delete(self, *args, **kwargs):
        self.photo.delete()
        super(EMGElectrodePlacement, self).delete(*args, **kwargs)


class EMGSurfacePlacement(EMGElectrodePlacement):
    start_posture = models.TextField(null=True, blank=True)
    orientation = models.TextField(null=True, blank=True)
    fixation_on_the_skin = models.TextField(null=True, blank=True)
    reference_electrode = models.TextField(null=True, blank=True)
    clinical_test = models.TextField(null=True, blank=True)


class EMGIntramuscularPlacement(EMGElectrodePlacement):
    method_of_insertion = models.TextField(null=True, blank=True)
    depth_of_insertion = models.TextField(null=True, blank=True)


class EMGNeedlePlacement(EMGElectrodePlacement):
    depth_of_insertion = models.TextField(null=True, blank=True)


class EMGSetting(models.Model):
    experiment = models.ForeignKey(Experiment)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey('self', null=True, related_name='children')
    acquisition_software_version = models.ForeignKey(SoftwareVersion)

    def __str__(self):
        return self.name


class EMGDigitalFilterSetting(models.Model):
    emg_setting = models.OneToOneField(EMGSetting, primary_key=True, related_name='emg_digital_filter_setting')
    filter_type = models.ForeignKey(FilterType)
    low_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGADConverterSetting(models.Model):
    emg_setting = models.OneToOneField(EMGSetting, primary_key=True, related_name='emg_ad_converter_setting')
    ad_converter = models.ForeignKey(ADConverter)
    sampling_rate = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGElectrodeSetting(models.Model):
    emg_setting = models.ForeignKey(EMGSetting, related_name='emg_electrode_settings')
    electrode = models.ForeignKey(ElectrodeModel)


class EMGPreamplifierSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(EMGElectrodeSetting,
                                                 primary_key=True, related_name='emg_preamplifier_setting')
    amplifier = models.ForeignKey(Amplifier)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGPreamplifierFilterSetting(models.Model):
    emg_preamplifier_filter_setting = models.OneToOneField(EMGPreamplifierSetting,
                                                           primary_key=True,
                                                           related_name='emg_preamplifier_filter_setting')
    low_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGAmplifierSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(EMGElectrodeSetting,
                                                 primary_key=True, related_name='emg_amplifier_setting')
    amplifier = models.ForeignKey(Amplifier)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGAnalogFilterSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(EMGAmplifierSetting,
                                                 primary_key=True, related_name='emg_analog_filter_setting')
    low_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    low_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_band_pass = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    high_notch = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])


class EMGElectrodePlacementSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(EMGElectrodeSetting,
                                                 primary_key=True, related_name='emg_electrode_placement_setting')
    emg_electrode_placement = models.ForeignKey(EMGElectrodePlacement)
    remarks = models.TextField(null=True, blank=True)
    muscle_side = models.ForeignKey(MuscleSide, null=True, blank=True)


class TMSSetting(models.Model):
    experiment = models.ForeignKey(Experiment)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey('self', null=True, related_name='children')

    def __str__(self):
        return self.name


class TMSDeviceSetting(models.Model):
    PULSE_STIMULUS_TYPES = (
        ("single_pulse", _("Single pulse")),
        ("paired_pulse", _("Paired pulse")),
        ("repetitive_pulse", _("Repetitive pulse"))
    )
    tms_setting = models.OneToOneField(TMSSetting, primary_key=True, related_name='tms_device_setting')
    tms_device = models.ForeignKey(TMSDevice)
    pulse_stimulus_type = models.CharField(null=True, blank=True, max_length=50, choices=PULSE_STIMULUS_TYPES)
    coil_model = models.ForeignKey(CoilModel)


def get_tms_brain_area_dir(instance, filename):
    return "tms_brain_area_files/%s/%s" % \
           (instance.id, filename)


class BrainAreaSystem(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class BrainAreaSystemPerspective(models.Model):
    brain_area_image = models.FileField(upload_to=get_tms_brain_area_dir, null=True, blank=True)
    brain_area_system = models.ForeignKey(BrainAreaSystem)


def get_tms_localization_system_dir(instance, filename):
    return "tms_localization_system_files/%s/%s" % \
           (instance.id, filename)


class BrainArea(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    brain_area_system = models.ForeignKey(BrainAreaSystem)

    def __str__(self):
        return self.name


class TMSLocalizationSystem(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    tms_localization_system_image = models.FileField(upload_to=get_tms_localization_system_dir, null=True, blank=True)
    brain_area = models.ForeignKey(BrainArea)

    def __str__(self):
        return self.name


class CoilOrientation(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class DirectionOfTheInducedCurrent(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Component(models.Model):
    COMPONENT_TYPES = (
        ("block", _("Set of steps")),
        ("instruction", _("Instruction")),
        ("pause", _("Pause")),
        ("questionnaire", _("Questionnaire")),
        ("stimulus", _("Stimulus")),
        ("task", _("Task for participant")),
        ("task_experiment", _("Task for experimenter")),
        ("eeg", _("EEG")),
        ("emg", _("EMG")),
        ("tms", _("TMS")),
        ("digital_game_phase", _("Digital game phase")),
    )

    identification = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    duration_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    duration_unit = models.CharField(null=True, blank=True, max_length=15, choices=TIME_UNITS)
    experiment = models.ForeignKey(Experiment, null=False)
    component_type = models.CharField(null=False, max_length=30, choices=COMPONENT_TYPES)


class Task(Component):
    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class TaskForTheExperimenter(Component):
    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Instruction(Component):
    text = models.TextField(null=False, blank=False)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Pause(Component):
    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


def get_stimulus_media_file_dir(instance, filename):
    return "stimulus_step/%s/%s" % \
           (instance.id, filename)


class Stimulus(Component):
    stimulus_type = models.ForeignKey(StimulusType, null=False, blank=False)
    media_file = models.FileField(upload_to=get_stimulus_media_file_dir, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Questionnaire(Component):
    survey = models.ForeignKey(Survey, null=False, blank=False, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Block(Component):
    SEQUENCE = 'sequence'
    PARALLEL_BLOCK = 'parallel_block'
    BLOCK_TYPES = ((SEQUENCE, _("Sequence")), (PARALLEL_BLOCK, _("Parallel")))
    number_of_mandatory_components = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    type = models.CharField(null=False, max_length=20,
                            choices=BLOCK_TYPES)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class EEG(Component):
    eeg_setting = models.ForeignKey(EEGSetting)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class EMG(Component):
    emg_setting = models.ForeignKey(EMGSetting)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class TMS(Component):
    tms_setting = models.ForeignKey(TMSSetting)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


def get_context_tree_dir(instance, filename):
    return "context_tree/%s/%s" % (instance.id, filename)


class ContextTree(models.Model):
    experiment = models.ForeignKey(Experiment)
    name = models.CharField(max_length=50)
    description = models.TextField()
    setting_text = models.TextField(null=True, blank=True)
    setting_file = models.FileField(upload_to=get_context_tree_dir, null=True, blank=True)

    def __str__(self):
        return self.name


class DigitalGamePhase(Component):
    software_version = models.ForeignKey(SoftwareVersion)
    context_tree = models.ForeignKey(ContextTree)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class ComponentConfiguration(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    number_of_repetitions = models.IntegerField(null=True, blank=True, default=1, validators=[MinValueValidator(1)])

    # These 2 interval fields are useful only when number_of_repetition is different from 1.
    interval_between_repetitions_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    interval_between_repetitions_unit = models.CharField(null=True, blank=True, max_length=15, choices=TIME_UNITS)

    component = models.ForeignKey(Component, null=False, related_name="configuration")
    # TODO Change to not null.
    parent = models.ForeignKey(Block, null=True, related_name='children')

    # This field is only useful for component configurations marked as fixed and inside a sequence. However, we leave it
    # as not null because we want the unique restriction of the pair (parent, order) to be applied in a database level.
    order = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1)])

    # This is null when the parent is a parallel block.
    random_position = models.NullBooleanField(blank=True)

    requires_start_and_end_datetime = models.BooleanField(default=False)

    class Meta:
        unique_together = ('parent', 'order',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and not self.order:
            top = ComponentConfiguration.objects.filter(parent=self.parent).order_by('-order').first()
            self.order = top.order + 1 if top else 1
        super(ComponentConfiguration, self).save()


class Group(models.Model):
    experiment = models.ForeignKey(Experiment, null=False, blank=False)
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=False, blank=False)
    classification_of_diseases = models.ManyToManyField(ClassificationOfDiseases)
    experimental_protocol = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL)


def get_dir(instance, filename):
    return "consent_forms/%s/%s/%s/%s" % \
           (instance.group.experiment.id, instance.group.id, instance.subject.id, filename)


def get_eeg_dir(instance, filename):
    return "eeg_data_files/%s/%s/%s/%s" % \
           (instance.group.experiment.id, instance.group.id, instance.subject.id, filename)


def get_data_file_dir(instance, filename):
    directory = 'data_files'
    if isinstance(instance, DataCollection):
        directory = path.join('data_collection_files',
                              str(instance.subject_of_group.group.experiment.id),
                              str(instance.subject_of_group.group.id),
                              str(instance.subject_of_group.subject.id),
                              str(instance.data_configuration_tree.id if instance.data_configuration_tree else 0))
        if isinstance(instance, EEGData):
            directory = path.join(directory, 'eeg')
        elif isinstance(instance, EMGData):
            directory = path.join(directory, 'emg')
        elif isinstance(instance, AdditionalData):
            directory = path.join(directory, 'additional')
    return path.join(directory, filename)


class SubjectOfGroup(models.Model):
    subject = models.ForeignKey(Subject, null=False, blank=False)
    group = models.ForeignKey(Group, null=False, blank=False)
    consent_form = models.FileField(upload_to=get_dir, null=True)

    class Meta:
        unique_together = ('subject', 'group',)


class DataConfigurationTree(models.Model):
    component_configuration = models.ForeignKey(ComponentConfiguration, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', null=True, related_name='children')


class SubjectStepData(models.Model):
    # data_configuration_tree null means that the DataCollection is associated to the whole experimental protocol
    data_configuration_tree = models.ForeignKey(DataConfigurationTree, null=True, blank=True)

    subject_of_group = models.ForeignKey(SubjectOfGroup)

    start_date = models.DateField(default=datetime.date.today, null=True, blank=True,
                                  validators=[validate_date_questionnaire_response])
    start_time = models.TimeField(null=True, blank=True)

    end_date = models.DateField(default=datetime.date.today, null=True, blank=True,
                                validators=[validate_date_questionnaire_response])
    end_time = models.TimeField(null=True, blank=True)


class DataCollection(models.Model):
    # data_configuration_tree null means that the DataCollection is associated to the whole experimental protocol
    data_configuration_tree = models.ForeignKey(DataConfigurationTree, null=True, blank=True)

    subject_of_group = models.ForeignKey(SubjectOfGroup)
    date = models.DateField(default=datetime.date.today, null=False,
                            validators=[validate_date_questionnaire_response])
    time = models.TimeField(null=True, blank=True)

    class Meta:
        abstract = True


class QuestionnaireResponse(DataCollection):
    token_id = models.IntegerField(null=False)
    questionnaire_responsible = models.ForeignKey(User, null=False, related_name="+")

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    class Meta:
        permissions = (
            ("view_questionnaireresponse", "Can view questionnaire response"),
        )

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return "token id: " + str(self.token_id)


class FileFormat(models.Model):

    # Code that NES knows the format and can handle the content.
    # E.g.: "NEO-RawBinarySignalIO", "other"
    nes_code = models.CharField(null=True, blank=True, max_length=50, unique=True)

    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name


class DataFile(models.Model):
    description = models.TextField(null=False, blank=False)
    file = models.FileField(upload_to=get_data_file_dir, null=False)
    file_format = models.ForeignKey(FileFormat, null=False, blank=False)
    file_format_description = models.TextField(null=True, blank=True, default='')

    class Meta:
        abstract = True

    def get_dir(self, filename):
        return "eeg_data_files/%s/%s/%s/%s" % \
               (self.group.experiment.id, self.group.id, self.subject.id, filename)


class EEGData(DataFile, DataCollection):
    eeg_setting = models.ForeignKey(EEGSetting)
    eeg_setting_reason_for_change = models.TextField(null=True, blank=True, default='')
    eeg_cap_size = models.ForeignKey(EEGCapSize, null=True, blank=True)

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.description

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class TMSData(DataCollection):
    tms_setting = models.ForeignKey(TMSSetting)
    resting_motor_threshold = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    test_pulse_intensity_of_simulation = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    second_test_pulse_intensity = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    interval_between_pulses = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    interval_between_pulses_unit = models.CharField(null=True, blank=True, max_length=15, choices=TIME_UNITS)
    # time_between_mep_trials_low = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    time_between_mep_trials = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    # time_between_mep_trials_high = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    time_between_mep_trials_unit = models.CharField(null=True, blank=True, max_length=15, choices=TIME_UNITS)
    repetitive_pulse_frequency = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    coil_orientation = models.ForeignKey(CoilOrientation, null=True, blank=True)
    coil_orientation_angle = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    direction_of_induced_current = models.ForeignKey(DirectionOfTheInducedCurrent, null=True, blank=True)
    description = models.TextField(null=False, blank=False)

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.description

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class HotSpot(models.Model):
    name = models.CharField(max_length=50)
    coordinate_x = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    coordinate_y = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    tms_data = models.OneToOneField(TMSData, primary_key=True)
    tms_localization_system = models.ForeignKey(TMSLocalizationSystem, related_name='hotspots')

    def __str__(self):
        return self.name


class AdditionalData(DataFile, DataCollection):

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.description

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class EMGData(DataFile, DataCollection):
    emg_setting = models.ForeignKey(EMGSetting)
    emg_setting_reason_for_change = models.TextField(null=True, blank=True, default='')

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.description

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class DigitalGamePhaseData(DataFile, DataCollection):
    sequence_used_in_context_tree = models.TextField(null=True, blank=True)

    # Audit trail - Simple History
    history = HistoricalRecords()
    # changed_by = models.ForeignKey('auth.User')

    def __str__(self):
        return self.description

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class EEGElectrodePositionCollectionStatus(models.Model):
    eeg_data = models.ForeignKey(EEGData, related_name='electrode_positions')
    eeg_electrode_position_setting = models.ForeignKey(EEGElectrodePositionSetting)
    worked = models.BooleanField()
    channel_index = models.IntegerField()

    class Meta:
        unique_together = ('eeg_data', 'channel_index')

    def __str__(self):
        return self.eeg_electrode_position_setting.eeg_electrode_position.name
