# -*- coding: UTF-8 -*-
import datetime
from os import path
from typing import Any, LiteralString

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage.filesystem import FileSystemStorage
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modeltranslation.manager import MultilingualManager
from patient.models import ClassificationOfDiseases, Patient
from simple_history.models import HistoricalRecords
from survey.models import Survey

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
    ("gigaohm", _("Gigaohm(s)")),
)


def validate_date_questionnaire_response(value):
    if value > datetime.date.today():
        raise ValidationError(_("Date cannot be greater than today's date."))


class StimulusType(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class ResearchProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    keywords = models.ManyToManyField(Keyword)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        permissions = (
            # ("view_researchproject", "Can view research project"),
            (
                "change_researchproject_from_others",
                "Can change research project created by others",
            ),
            ("change_researchproject_owner", "Can change research project owner"),
        )


def get_experiment_dir(instance, filename):
    return "experiment_files/%s/%s" % (instance.id, filename)


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=255, blank=False)
    description = models.TextField(null=False, blank=False)
    research_project = models.ForeignKey(
        ResearchProject, on_delete=models.CASCADE, null=False, blank=False
    )
    is_public = models.BooleanField(default=False)
    data_acquisition_is_concluded = models.BooleanField(default=False)

    source_code_url = models.URLField(null=True, blank=True)
    ethics_committee_project_url = models.URLField(
        _("URL of the project approved by the ethics committee"), null=True, blank=True
    )
    ethics_committee_project_file = models.FileField(
        _("Project file approved by the ethics committee"),
        upload_to=get_experiment_dir,
        null=True,
        blank=True,
    )
    last_update = models.DateTimeField(auto_now=True)
    last_sending = models.DateTimeField(null=True)

    # Audit trail - Simple History
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.title

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value) -> None:
    #     self.changed_by = value


class ExperimentResearcher(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="researchers"
    )
    researcher = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_index = models.IntegerField(null=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        if not self.pk and not self.channel_index:
            top = (
                ExperimentResearcher.objects.filter(experiment=self.experiment)
                .order_by("-channel_index")
                .first()
            )
            if isinstance(top, models.IntegerField):
                self.channel_index = top.channel_index + 1
            else:
                self.channel_index = 1

        super(ExperimentResearcher, self).save()


class PublicationType(models.Model):
    name = models.CharField(max_length=50)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class Publication(models.Model):
    title = models.CharField(max_length=255)
    citation = models.TextField()
    url = models.URLField(null=True, blank=True)
    experiments = models.ManyToManyField(Experiment)
    publication_type = models.ForeignKey(
        PublicationType, null=True, blank=True, on_delete=models.CASCADE
    )


class Manufacturer(models.Model):
    name = models.CharField(max_length=50)  # TODO: possibly make unique

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):  # type: ignore [django-manager-missing]
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    EQUIPMENT_TYPES = (
        ("eeg_machine", _("EEG Machine")),
        ("amplifier", _("Amplifier")),
        ("eeg_solution", _("EEG Solution")),
        ("filter", _("Filter")),
        ("eeg_electrode_net", _("EEG Electrode Net")),
        ("ad_converter", _("A/D Converter")),
        ("tms_device", _("TMS device")),
        ("stimuli_eq", _("Stimuli Equipment")),
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, related_name="set_of_equipment"
    )
    equipment_type = models.CharField(
        null=True, blank=True, max_length=50, choices=EQUIPMENT_TYPES
    )
    identification = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return self.identification

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipment")

        permissions = (("register_equipment", "Can register equipment"),)


class AmplifierDetectionType(models.Model):
    name = models.CharField(max_length=150)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class TetheringSystem(models.Model):
    name = models.CharField(max_length=150)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class Amplifier(Equipment):
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    number_of_channels = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    common_mode_rejection_ratio = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    input_impedance = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    input_impedance_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=IMPEDANCE_UNIT
    )
    amplifier_detection_type = models.ForeignKey(
        AmplifierDetectionType, on_delete=models.CASCADE, null=True, blank=True
    )
    tethering_system = models.ForeignKey(
        TetheringSystem, on_delete=models.CASCADE, null=True, blank=True
    )


class EEGSolution(models.Model):
    name = models.CharField(max_length=150)
    components = models.TextField(null=True, blank=True)
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        null=False,
        related_name="set_of_solution",
    )


class FilterType(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self) -> str:
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class ElectrodeConfiguration(models.Model):
    name = models.CharField(max_length=150)

    objects: MultilingualManager

    def __str__(self) -> str:
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
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, null=True, blank=True
    )
    usability = models.CharField(
        null=True, blank=True, max_length=50, choices=USABILITY_TYPES
    )
    impedance = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    impedance_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=IMPEDANCE_UNIT
    )
    tags = models.ManyToManyField(Tag)
    inter_electrode_distance = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    inter_electrode_distance_unit = models.CharField(
        null=True, blank=True, max_length=10, choices=ELECTRODE_DISTANCE_UNIT
    )
    electrode_configuration = models.ForeignKey(
        ElectrodeConfiguration, on_delete=models.CASCADE, null=True, blank=True
    )
    electrode_type = models.CharField(max_length=50, choices=ELECTRODE_TYPES)

    def __str__(self) -> str:
        return self.name


class MeasureSystem(models.Model):  # type: ignore [django-manager-missing]
    name = models.CharField(max_length=150)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class MeasureUnit(models.Model):
    name = models.CharField(max_length=150)
    measure_system = models.ForeignKey(MeasureSystem, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class ElectrodeShape(models.Model):
    name = models.CharField(max_length=150)
    measure_systems = models.ManyToManyField(MeasureSystem)

    objects: MultilingualManager

    def __str__(self) -> str:
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
    electrode_shape = models.ForeignKey(ElectrodeShape, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(ElectrodeModel, self).save(*args, **kwargs)


class ElectrodeSurfaceMeasure(models.Model):
    electrode_surface = models.ForeignKey(SurfaceElectrode, on_delete=models.CASCADE)
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0)])


class IntramuscularElectrode(ElectrodeModel):
    STRAND_TYPES = (
        ("single", _("Single")),
        ("multi", _("Multi")),
    )
    strand = models.CharField(max_length=20, choices=STRAND_TYPES)
    insulation_material = models.ForeignKey(
        Material, on_delete=models.CASCADE, null=True, blank=True
    )
    length_of_exposed_tip = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(ElectrodeModel, self).save(*args, **kwargs)


class NeedleElectrode(ElectrodeModel):
    SIZE_UNIT = (
        ("mm", _("millimeter(s)")),
        ("cm", _("centimeter(s)")),
    )
    size = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    size_unit = models.CharField(
        max_length=10, choices=SIZE_UNIT, null=True, blank=True
    )
    number_of_conductive_contact_points_at_the_tip = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    size_of_conductive_contact_points_at_the_tip = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(ElectrodeModel, self).save(*args, **kwargs)


class EEGElectrodeNet(Equipment):
    electrode_model_default = models.ForeignKey(
        ElectrodeModel, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.identification


class EEGElectrodeCap(EEGElectrodeNet):
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, null=True, blank=True
    )


class EEGCapSize(models.Model):
    eeg_electrode_cap = models.ForeignKey(EEGElectrodeCap, on_delete=models.CASCADE)
    size = models.CharField(max_length=30)
    electrode_adjacent_distance = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def __str__(self) -> str:
        return self.size


def get_eeg_electrode_system_dir(instance, filename):
    return "eeg_electrode_system_files/%s/%s" % (instance.id, filename)


class EEGElectrodeLocalizationSystem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    map_image_file = models.FileField(
        upload_to=get_eeg_electrode_system_dir, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        self.map_image_file.delete()
        super(EEGElectrodeLocalizationSystem, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            saved_file = self.map_image_file
            self.map_image_file = None
            super(EEGElectrodeLocalizationSystem, self).save(*args, **kwargs)
            self.map_image_file = saved_file
        else:
            super(EEGElectrodeLocalizationSystem, self).save(*args, **kwargs)


class EEGElectrodePosition(models.Model):
    eeg_electrode_localization_system = models.ForeignKey(
        EEGElectrodeLocalizationSystem,
        on_delete=models.CASCADE,
        related_name="electrode_positions",
    )
    name = models.CharField(max_length=150)
    coordinate_x = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    coordinate_y = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    position_reference = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    channel_default_index = models.IntegerField()

    class Meta:
        unique_together = (
            "eeg_electrode_localization_system",
            "channel_default_index",
        )

    def __str__(self) -> str:
        return self.eeg_electrode_localization_system.name + " - " + self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk and not self.channel_default_index:
            top = (
                EEGElectrodePosition.objects.filter(
                    eeg_electrode_localization_system=self.eeg_electrode_localization_system
                )
                .order_by("-channel_default_index")
                .first()
            )
            self.channel_default_index = top.channel_default_index + 1 if top else 1
        super(EEGElectrodePosition, self).save()


class EEGElectrodeNetSystem(models.Model):
    eeg_electrode_net = models.ForeignKey(
        EEGElectrodeNet,
        on_delete=models.CASCADE,
        related_name="set_of_electrode_net_system",
    )
    eeg_electrode_localization_system = models.ForeignKey(
        EEGElectrodeLocalizationSystem,
        on_delete=models.CASCADE,
        related_name="set_of_electrode_net_system",
    )


class CoilShape(models.Model):
    name = models.CharField(max_length=150)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class CoilModel(models.Model):
    COIL_DESIGN_OPTIONS = (
        ("air_core_coil", _("Air core coil")),
        ("solid_core_coil", _("Solid core coil")),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    coil_shape = models.ForeignKey(CoilShape, on_delete=models.CASCADE)
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, null=True, blank=True
    )
    coil_design = models.CharField(
        null=True, blank=True, max_length=50, choices=COIL_DESIGN_OPTIONS
    )

    def __str__(self) -> str:
        return self.name


class TMSDevice(Equipment):
    PULSE_TYPES = (
        ("monophase", _("Monophase")),
        ("biphase", _("Biphase")),
    )

    pulse_type = models.CharField(
        null=True, blank=True, max_length=50, choices=PULSE_TYPES
    )

    def __str__(self) -> str:
        return self.identification


class StimuliEq(Equipment):
    def __str__(self) -> str:
        return self.identification


class StimuliEqSetting(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    stimuli_eq = models.ForeignKey(StimuliEq, on_delete=models.CASCADE)
    description = models.TextField()

    copied_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    def __str__(self) -> str:
        return str(self.name + ":" + self.stimuli_eq.identification)

    def save(self, *args, **kwargs) -> None:
        super(StimuliEqSetting, self).save(*args, **kwargs)
        self.experiment.save()


class EEGSetting(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super(EEGSetting, self).save(*args, **kwargs)
        self.experiment.save()


class EEGAmplifierSetting(models.Model):
    eeg_setting = models.OneToOneField(
        EEGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="eeg_amplifier_setting",
    )
    eeg_amplifier = models.ForeignKey(Amplifier, on_delete=models.CASCADE)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    sampling_rate = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    number_of_channels_used = models.IntegerField(
        null=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EEGAmplifierSetting, self).save(*args, **kwargs)
        self.eeg_setting.experiment.save()


class EEGSolutionSetting(models.Model):
    eeg_setting = models.OneToOneField(
        EEGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="eeg_solution_setting",
    )
    eeg_solution = models.ForeignKey(EEGSolution, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(EEGSolutionSetting, self).save(*args, **kwargs)
        self.eeg_setting.experiment.save()


class EEGFilterSetting(models.Model):
    eeg_setting = models.OneToOneField(
        EEGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="eeg_filter_setting",
    )
    eeg_filter_type = models.ForeignKey(FilterType, on_delete=models.CASCADE)
    high_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    order = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EEGFilterSetting, self).save(*args, **kwargs)
        self.eeg_setting.experiment.save()


class EEGElectrodeLayoutSetting(models.Model):
    eeg_setting = models.OneToOneField(
        EEGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="eeg_electrode_layout_setting",
    )
    eeg_electrode_net_system = models.ForeignKey(
        EEGElectrodeNetSystem, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs) -> None:
        super(EEGElectrodeLayoutSetting, self).save(*args, **kwargs)
        self.eeg_setting.experiment.save()


class EEGElectrodePositionSetting(models.Model):
    eeg_electrode_layout_setting = models.ForeignKey(
        EEGElectrodeLayoutSetting,
        on_delete=models.CASCADE,
        related_name="positions_setting",
    )
    eeg_electrode_position = models.ForeignKey(
        EEGElectrodePosition, on_delete=models.CASCADE
    )
    used = models.BooleanField()
    electrode_model = models.ForeignKey(ElectrodeModel, on_delete=models.CASCADE)
    channel_index = models.IntegerField()

    class Meta:
        unique_together = (
            "eeg_electrode_layout_setting",
            "channel_index",
        )

    def save(self, *args, **kwargs) -> None:
        super(EEGElectrodePositionSetting, self).save(*args, **kwargs)
        self.eeg_electrode_layout_setting.eeg_setting.experiment.save()


class Software(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class SoftwareVersion(models.Model):
    software = models.ForeignKey(
        Software, on_delete=models.CASCADE, related_name="versions"
    )
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.software.name + " - " + self.name


class ADConverter(Equipment):
    signal_to_noise_rate = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    sampling_rate = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    resolution = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )


class StandardizationSystem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Muscle(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name


class MuscleSubdivision(models.Model):
    name = models.CharField(max_length=150)
    muscle = models.ForeignKey(Muscle, on_delete=models.CASCADE)
    anatomy_origin = models.TextField(null=True, blank=True)
    anatomy_insertion = models.TextField(null=True, blank=True)
    anatomy_function = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.muscle.name + " - " + self.name


class MuscleSide(models.Model):
    name = models.CharField(max_length=150)
    muscle = models.ForeignKey(Muscle, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


def get_emg_placement_dir(instance, filename) -> str:
    return "emg_placement_files/%s/%s" % (instance.standardization_system.id, filename)


class EMGElectrodePlacement(models.Model):
    PLACEMENT_TYPES = (
        ("surface", _("Surface")),
        ("intramuscular", _("Intramuscular")),
        ("needle", _("Needle")),
    )
    standardization_system = models.ForeignKey(
        StandardizationSystem,
        on_delete=models.CASCADE,
        related_name="electrode_placements",
    )
    muscle_subdivision = models.ForeignKey(MuscleSubdivision, on_delete=models.CASCADE)
    placement_reference = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    photo = models.FileField(upload_to=get_emg_placement_dir, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    placement_type = models.CharField(max_length=50, choices=PLACEMENT_TYPES)

    def __str__(self) -> str:
        return (
            self.standardization_system.name
            + " - "
            + self.muscle_subdivision.muscle.name
            + " - "
            + self.muscle_subdivision.name
        )

    def delete(self, *args, **kwargs) -> Any:
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
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )
    acquisition_software_version = models.ForeignKey(
        SoftwareVersion, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super(EMGSetting, self).save(*args, **kwargs)
        self.experiment.save()


class EMGDigitalFilterSetting(models.Model):
    emg_setting = models.OneToOneField(
        EMGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_digital_filter_setting",
    )
    filter_type = models.ForeignKey(FilterType, on_delete=models.CASCADE)
    low_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    order = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EMGDigitalFilterSetting, self).save(*args, **kwargs)
        self.emg_setting.experiment.save()


class EMGADConverterSetting(models.Model):
    emg_setting = models.OneToOneField(
        EMGSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_ad_converter_setting",
    )
    ad_converter = models.ForeignKey(ADConverter, on_delete=models.CASCADE)
    sampling_rate = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EMGADConverterSetting, self).save(*args, **kwargs)
        self.emg_setting.experiment.save()


class EMGElectrodeSetting(models.Model):
    emg_setting = models.ForeignKey(
        EMGSetting, on_delete=models.CASCADE, related_name="emg_electrode_settings"
    )
    electrode = models.ForeignKey(ElectrodeModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(EMGElectrodeSetting, self).save(*args, **kwargs)
        self.emg_setting.experiment.save()


class EMGPreamplifierSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(
        EMGElectrodeSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_preamplifier_setting",
    )
    amplifier = models.ForeignKey(Amplifier, on_delete=models.CASCADE)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs) -> None:
        super(EMGPreamplifierSetting, self).save(*args, **kwargs)
        self.emg_electrode_setting.emg_setting.experiment.save()


class EMGPreamplifierFilterSetting(models.Model):
    emg_preamplifier_filter_setting = models.OneToOneField(
        EMGPreamplifierSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_preamplifier_filter_setting",
    )
    low_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    order = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EMGPreamplifierFilterSetting, self).save(*args, **kwargs)
        self.emg_preamplifier_filter_setting.emg_electrode_setting.emg_setting.experiment.save()


class EMGAmplifierSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(
        EMGElectrodeSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_amplifier_setting",
    )
    amplifier = models.ForeignKey(Amplifier, on_delete=models.CASCADE)
    gain = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs) -> None:
        super(EMGAmplifierSetting, self).save(*args, **kwargs)
        self.emg_electrode_setting.emg_setting.experiment.save()


class EMGAnalogFilterSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(
        EMGAmplifierSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_analog_filter_setting",
    )
    low_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    low_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_band_pass = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    high_notch = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    order = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs) -> None:
        super(EMGAnalogFilterSetting, self).save(*args, **kwargs)
        self.emg_electrode_setting.emg_electrode_setting.emg_setting.experiment.save()


class EMGElectrodePlacementSetting(models.Model):
    emg_electrode_setting = models.OneToOneField(
        EMGElectrodeSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="emg_electrode_placement_setting",
    )
    emg_electrode_placement = models.ForeignKey(
        EMGElectrodePlacement, on_delete=models.CASCADE
    )
    remarks = models.TextField(null=True, blank=True)
    muscle_side = models.ForeignKey(
        MuscleSide, on_delete=models.CASCADE, null=True, blank=True
    )

    def save(self, *args, **kwargs) -> None:
        super(EMGElectrodePlacementSetting, self).save(*args, **kwargs)
        self.emg_electrode_setting.emg_setting.experiment.save()


class TMSSetting(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        super(TMSSetting, self).save(*args, **kwargs)
        self.experiment.save()


class TMSDeviceSetting(models.Model):
    PULSE_STIMULUS_TYPES = (
        ("single_pulse", _("Single pulse")),
        ("paired_pulse", _("Paired pulse")),
        ("repetitive_pulse", _("Repetitive pulse")),
    )
    tms_setting = models.OneToOneField(
        TMSSetting,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="tms_device_setting",
    )
    tms_device = models.ForeignKey(TMSDevice, on_delete=models.CASCADE)
    pulse_stimulus_type = models.CharField(
        null=True, blank=True, max_length=50, choices=PULSE_STIMULUS_TYPES
    )
    coil_model = models.ForeignKey(CoilModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(TMSDeviceSetting, self).save(*args, **kwargs)
        self.tms_setting.experiment.save()


def get_tms_brain_area_dir(instance, filename):
    return "tms_brain_area_files/%s/%s" % (instance.id, filename)


class BrainAreaSystem(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class BrainAreaSystemPerspective(models.Model):
    brain_area_image = models.FileField(
        upload_to=get_tms_brain_area_dir, null=True, blank=True
    )
    brain_area_system = models.ForeignKey(BrainAreaSystem, on_delete=models.CASCADE)


def get_tms_localization_system_dir(instance, filename):
    return "tms_localization_system_files/%s/%s" % (instance.id, filename)


class BrainArea(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    brain_area_system = models.ForeignKey(BrainAreaSystem, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class TMSLocalizationSystem(models.Model):
    name = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    tms_localization_system_image = models.FileField(
        upload_to=get_tms_localization_system_dir, null=True, blank=True
    )
    brain_area = models.ForeignKey(BrainArea, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        self.tms_localization_system_image.delete()
        super(TMSLocalizationSystem, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            saved_file = self.tms_localization_system_image
            self.tms_localization_system_image = None
            super(TMSLocalizationSystem, self).save(*args, **kwargs)
            self.tms_localization_system_image = saved_file
        else:
            super(TMSLocalizationSystem, self).save(*args, **kwargs)


class CoilOrientation(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name


class DirectionOfTheInducedCurrent(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name


class Component(models.Model):
    BLOCK = "block"
    INSTRUCTION = "instruction"
    PAUSE = "pause"
    QUESTIONNAIRE = "questionnaire"
    STIMULUS = "stimulus"
    TASK = "task"
    TASK_EXPERIMENT = "task_experiment"
    EEG = "eeg"
    EMG = "emg"
    TMS = "tms"
    DIGITAL_GAME_PHASE = "digital_game_phase"
    MEDIA_COLLECTION = "media_collection"
    GENERIC_DATA_COLLECTION = "generic_data_collection"
    COMPONENT_TYPES = (
        (BLOCK, _("Set of steps")),
        (INSTRUCTION, _("Instruction")),
        (PAUSE, _("Pause")),
        (QUESTIONNAIRE, _("Questionnaire")),
        (STIMULUS, _("Stimulus")),
        (TASK, _("Task for participant")),
        (TASK_EXPERIMENT, _("Task for experimenter")),
        (EEG, _("EEG")),
        (EMG, _("EMG")),
        (TMS, _("TMS")),
        (DIGITAL_GAME_PHASE, _("Goalkeeper game phase")),
        (GENERIC_DATA_COLLECTION, _("Generic data collection")),
        (MEDIA_COLLECTION, _("Media collection")),
    )

    identification = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    duration_value = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    duration_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=TIME_UNITS
    )
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="components"
    )
    component_type = models.CharField(max_length=30, choices=COMPONENT_TYPES)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)
        self.experiment.save()


def get_step_file_dir(instance, filename) -> LiteralString:
    return "step/%s/%s" % (instance.component.id, filename)


class ComponentAdditionalFile(models.Model):
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="component_additional_files"
    )
    file = models.FileField(upload_to=get_step_file_dir)


class Task(Component):
    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class TaskForTheExperimenter(Component):
    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class Instruction(Component):
    text = models.TextField(null=False, blank=False)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class Pause(Component):
    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


def get_stimulus_media_file_dir(instance, filename) -> LiteralString:
    return "stimulus_step/%s/%s" % (instance.id, filename)


class Stimulus(Component):
    stimulus_type = models.ForeignKey(
        StimulusType, on_delete=models.CASCADE, null=False, blank=False
    )
    media_file = models.FileField(
        upload_to=get_stimulus_media_file_dir, null=True, blank=True
    )

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class Questionnaire(Component):
    survey = models.ForeignKey(
        Survey, null=False, blank=False, on_delete=models.PROTECT
    )

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class Block(Component):
    SEQUENCE = "sequence"
    PARALLEL_BLOCK = "parallel_block"
    BLOCK_TYPES = ((SEQUENCE, _("Sequence")), (PARALLEL_BLOCK, _("Parallel")))
    number_of_mandatory_components = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    type = models.CharField(null=False, max_length=20, choices=BLOCK_TYPES)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class EEG(Component):
    eeg_setting = models.ForeignKey(EEGSetting, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class EMG(Component):
    emg_setting = models.ForeignKey(EMGSetting, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class TMS(Component):
    tms_setting = models.ForeignKey(TMSSetting, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class InformationType(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class InformationTypeMedia(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class GenericDataCollection(Component):
    information_type = models.ForeignKey(
        InformationType, on_delete=models.CASCADE, null=False, blank=False
    )

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class MediaCollection(Component):
    information_type_media = models.ForeignKey(
        InformationTypeMedia, on_delete=models.CASCADE, null=False, blank=False
    )

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


def get_context_tree_dir(instance, filename):
    return "context_tree/%s/%s" % (instance.id, filename)


class ContextTree(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    setting_text = models.TextField(null=True, blank=True)
    setting_file = models.FileField(
        upload_to=get_context_tree_dir, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        self.setting_file.delete()
        super(ContextTree, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        if self.pk is None:
            saved_file = self.setting_file
            self.setting_file = None
            super(ContextTree, self).save(*args, **kwargs)
            self.setting_file = saved_file
        else:
            super(ContextTree, self).save(*args, **kwargs)

        self.experiment.save()


class DigitalGamePhase(Component):
    software_version = models.ForeignKey(SoftwareVersion, on_delete=models.CASCADE)
    context_tree = models.ForeignKey(ContextTree, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        super(Component, self).save(*args, **kwargs)


class ComponentConfiguration(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    number_of_repetitions = models.IntegerField(
        null=True, blank=True, default=1, validators=[MinValueValidator(1)]
    )

    # These 2 interval fields are useful only when number_of_repetition is
    # different from 1.
    interval_between_repetitions_value = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    interval_between_repetitions_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=TIME_UNITS
    )

    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, null=False, related_name="configuration"
    )
    # TODO Change to not null.
    parent = models.ForeignKey(
        Block, on_delete=models.CASCADE, null=True, related_name="children"
    )

    # This field is only useful for component configurations marked as fixed
    # and inside a sequence. However, we leave it as not null because we
    # want the unique restriction of the pair (parent, order) to be applied
    # in a database level.
    order = models.IntegerField(
        null=False, blank=False, validators=[MinValueValidator(1)]
    )

    # This is null when the parent is a parallel block.
    random_position = models.BooleanField(blank=True, null=True)

    requires_start_and_end_datetime = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "parent",
            "order",
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk and not self.order:
            top = (
                ComponentConfiguration.objects.filter(parent=self.parent)
                .order_by("-order")
                .first()
            )
            self.order = top.order + 1 if top else 1
        super(ComponentConfiguration, self).save()
        self.component.experiment.save()


class Group(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="groups",
    )
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=False, blank=False)
    code = models.CharField(
        _("Code"), null=True, blank=True, max_length=150, unique=True
    )
    classification_of_diseases = models.ManyToManyField(ClassificationOfDiseases)
    experimental_protocol = models.ForeignKey(
        Component, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Group")

    def save(self, *args, **kwargs) -> None:
        super(Group, self).save(*args, **kwargs)
        self.experiment.save()


def get_dir(instance, filename):
    return "consent_forms/%s/%s/%s/%s" % (
        instance.group.experiment.id,
        instance.group.id,
        instance.subject.id,
        filename,
    )


def get_eeg_dir(instance, filename):
    return "eeg_data_files/%s/%s/%s/%s" % (
        instance.group.experiment.id,
        instance.group.id,
        instance.subject.id,
        filename,
    )


def get_data_file_dir(instance, filename):
    directory = "data_files"

    if isinstance(instance, EEGFile):
        directory = path.join(
            "data_collection_files",
            str(instance.eeg_data.subject_of_group.group.experiment.id),
            str(instance.eeg_data.subject_of_group.group.id),
            str(instance.eeg_data.subject_of_group.subject.id),
            str(
                instance.eeg_data.data_configuration_tree.id
                if instance.eeg_data.data_configuration_tree
                else 0
            ),
            "eeg",
        )

    elif isinstance(instance, EMGFile):
        directory = path.join(
            "data_collection_files",
            str(instance.emg_data.subject_of_group.group.experiment.id),
            str(instance.emg_data.subject_of_group.group.id),
            str(instance.emg_data.subject_of_group.subject.id),
            str(
                instance.emg_data.data_configuration_tree.id
                if instance.emg_data.data_configuration_tree
                else 0
            ),
            "emg",
        )

    elif isinstance(instance, AdditionalDataFile):
        directory = path.join(
            "data_collection_files",
            str(instance.additional_data.subject_of_group.group.experiment.id),
            str(instance.additional_data.subject_of_group.group.id),
            str(instance.additional_data.subject_of_group.subject.id),
            str(
                instance.additional_data.data_configuration_tree.id
                if instance.additional_data.data_configuration_tree
                else 0
            ),
            "additional",
        )

    elif isinstance(instance, GenericDataCollectionFile):
        directory = path.join(
            "data_collection_files",
            str(
                instance.generic_data_collection_data.subject_of_group.group.experiment.id
            ),
            str(instance.generic_data_collection_data.subject_of_group.group.id),
            str(instance.generic_data_collection_data.subject_of_group.subject.id),
            str(
                instance.generic_data_collection_data.data_configuration_tree.id
                if instance.generic_data_collection_data.data_configuration_tree
                else 0
            ),
            "generic_data_collection",
        )

    elif isinstance(instance, MediaCollectionFile):
        directory = path.join(
            "data_collection_files",
            str(instance.media_collection_data.subject_of_group.group.experiment.id),
            str(instance.media_collection_data.subject_of_group.group.id),
            str(instance.media_collection_data.subject_of_group.subject.id),
            str(
                instance.media_collection_data.data_configuration_tree.id
                if instance.media_collection_data.data_configuration_tree
                else 0
            ),
            "media_collection",
        )

    elif isinstance(instance, DigitalGamePhaseFile):
        directory = path.join(
            "data_collection_files",
            str(instance.digital_game_phase_data.subject_of_group.group.experiment.id),
            str(instance.digital_game_phase_data.subject_of_group.group.id),
            str(instance.digital_game_phase_data.subject_of_group.subject.id),
            str(
                instance.digital_game_phase_data.data_configuration_tree.id
                if instance.digital_game_phase_data.data_configuration_tree
                else 0
            ),
            "digital_game_phase",
        )

    # TODO (NES-987): see backlog
    # elif isinstance(instance, HotSpot):
    #     directory = path.join(
    #         'data_collection_files',
    #         str(instance.tms_data.subject_of_group.group.experiment.id),
    #         str(instance.tms_data.subject_of_group.group.id),
    #         str(instance.tms_data.subject_of_group.subject.id),
    #         str(instance.tms_data.data_configuration_tree.id if instance.tms_data.data_configuration_tree else 0),
    #         'hot_spot_map'
    #     )

    return path.join(directory, filename)


class Subject(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


class SubjectOfGroup(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, null=False, blank=False
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)
    consent_form = models.FileField(upload_to=get_dir, null=True)

    class Meta:
        unique_together = (
            "subject",
            "group",
        )

    def save(self, *args, **kwargs) -> None:
        super(SubjectOfGroup, self).save(*args, **kwargs)
        self.group.experiment.save()


class DataConfigurationTree(models.Model):
    component_configuration = models.ForeignKey(
        ComponentConfiguration, on_delete=models.PROTECT
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )
    code = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        super(DataConfigurationTree, self).save(*args, **kwargs)
        self.component_configuration.component.experiment.save()


class SubjectStepData(models.Model):
    # data_configuration_tree null means that the DataCollection is
    # associated to the whole experimental protocol
    data_configuration_tree = models.ForeignKey(
        DataConfigurationTree, on_delete=models.CASCADE, null=True, blank=True
    )

    subject_of_group = models.ForeignKey(SubjectOfGroup, on_delete=models.CASCADE)

    start_date = models.DateField(
        default=datetime.date.today,
        null=True,
        blank=True,
        validators=[validate_date_questionnaire_response],
    )
    start_time = models.TimeField(null=True, blank=True)

    end_date = models.DateField(
        default=datetime.date.today,
        null=True,
        blank=True,
        validators=[validate_date_questionnaire_response],
    )
    end_time = models.TimeField(null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        super(SubjectStepData, self).save(*args, **kwargs)
        self.subject_of_group.group.experiment.save()


class DataCollection(models.Model):
    # data_configuration_tree null means that the DataCollection is associated
    # to the whole experimental protocol
    data_configuration_tree = models.ForeignKey(
        DataConfigurationTree, on_delete=models.CASCADE, null=True, blank=True
    )

    subject_of_group = models.ForeignKey(SubjectOfGroup, on_delete=models.CASCADE)
    date = models.DateField(
        default=datetime.date.today,
        null=False,
        validators=[validate_date_questionnaire_response],
    )
    time = models.TimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        super(DataCollection, self).save(*args, **kwargs)
        self.subject_of_group.group.experiment.save()


class QuestionnaireResponse(DataCollection):
    token_id = models.IntegerField(null=False)
    questionnaire_responsible = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name="+"
    )
    history = HistoricalRecords()
    is_completed = models.CharField(max_length=50, default="")

    class Meta:
        permissions = (
            # ('view_questionnaireresponse', 'Can view questionnaire response'),
        )

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value

    def __str__(self) -> str:
        return "token id: " + str(self.token_id)


class FileFormat(models.Model):
    # Code that NES knows the format and can handle the content.
    # E.g.: "NEO-RawBinarySignalIO", "other"
    nes_code = models.CharField(null=True, blank=True, max_length=50, unique=True)

    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class SourceCodeFileFormat(models.Model):
    nes_code = models.CharField(null=True, blank=True, max_length=50, unique=True)

    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    # tags = models.ManyToManyField(Tag)

    objects: MultilingualManager

    def __str__(self) -> str:
        return self.name


class DataFile(models.Model):
    description = models.TextField(null=False, blank=False)
    file_format = models.ForeignKey(
        FileFormat, on_delete=models.CASCADE, null=False, blank=False
    )
    file_format_description = models.TextField(null=True, blank=True, default="")

    class Meta:
        abstract = True


class SourceCode(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    description = models.TextField()

    source_code_data = models.ForeignKey(
        SourceCodeFileFormat, on_delete=models.CASCADE, related_name="source_code_files"
    )
    file = models.FileField(upload_to=get_experiment_dir)

    history = HistoricalRecords()

    copied_from = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="children"
    )

    def __str__(self) -> str:
        return self.name

    # def save(self, *args, **kwargs) -> None:
    #     super(SourceCode, self).save(*args, **kwargs)
    #     self.experiment.save()

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class EEGData(DataFile, DataCollection):
    eeg_setting = models.ForeignKey(EEGSetting, on_delete=models.CASCADE)
    eeg_setting_reason_for_change = models.TextField(null=True, blank=True, default="")
    eeg_cap_size = models.ForeignKey(
        EEGCapSize, on_delete=models.CASCADE, null=True, blank=True
    )

    # changed_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self) -> models.ForeignKey:
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value) -> None:
    #     self.changed_by = value


class TMSData(DataCollection):
    tms_setting = models.ForeignKey(TMSSetting, on_delete=models.CASCADE)
    resting_motor_threshold = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    test_pulse_intensity_of_simulation = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    second_test_pulse_intensity = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    interval_between_pulses = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    interval_between_pulses_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=TIME_UNITS
    )
    time_between_mep_trials = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    time_between_mep_trials_unit = models.CharField(
        null=True, blank=True, max_length=15, choices=TIME_UNITS
    )
    repetitive_pulse_frequency = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    coil_orientation = models.ForeignKey(
        CoilOrientation, on_delete=models.CASCADE, null=True, blank=True
    )
    coil_orientation_angle = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    direction_of_induced_current = models.ForeignKey(
        DirectionOfTheInducedCurrent, on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField(null=False, blank=False)

    # Audit trail - Simple History
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class HotSpot(models.Model):
    name = models.CharField(max_length=50)
    coordinate_x = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    coordinate_y = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    hot_spot_map = models.FileField(upload_to=get_data_file_dir, null=True, blank=True)
    tms_data = models.OneToOneField(TMSData, on_delete=models.CASCADE, primary_key=True)
    tms_localization_system = models.ForeignKey(
        TMSLocalizationSystem, on_delete=models.CASCADE, related_name="hotspots"
    )

    def __str__(self) -> str:
        return self.name


class AdditionalData(DataFile, DataCollection):
    # Audit trail - Simple History
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class EMGData(DataFile, DataCollection):
    emg_setting = models.ForeignKey(EMGSetting, on_delete=models.CASCADE)
    emg_setting_reason_for_change = models.TextField(null=True, blank=True, default="")

    # Audit trail - Simple History
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class DigitalGamePhaseData(DataFile, DataCollection):
    sequence_used_in_context_tree = models.TextField(null=True, blank=True)

    # Audit trail - Simple History
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class GenericDataCollectionData(DataFile, DataCollection):
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class MediaCollectionData(DataFile, DataCollection):
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.description

    # @property
    # def _history_user(self):
    #     return self.changed_by

    # @_history_user.setter
    # def _history_user(self, value):
    #     self.changed_by = value


class EEGFile(models.Model):
    eeg_data = models.ForeignKey(
        EEGData, on_delete=models.CASCADE, related_name="eeg_files"
    )
    file = models.FileField(upload_to=get_data_file_dir)


class EMGFile(models.Model):
    emg_data = models.ForeignKey(
        EMGData, on_delete=models.CASCADE, related_name="emg_files"
    )
    file = models.FileField(upload_to=get_data_file_dir)


class AdditionalDataFile(models.Model):
    additional_data = models.ForeignKey(
        AdditionalData, on_delete=models.CASCADE, related_name="additional_data_files"
    )
    file = models.FileField(upload_to=get_data_file_dir)


class DigitalGamePhaseFile(models.Model):
    digital_game_phase_data = models.ForeignKey(
        DigitalGamePhaseData,
        on_delete=models.CASCADE,
        related_name="digital_game_phase_files",
    )
    file = models.FileField(upload_to=get_data_file_dir)


class GenericDataCollectionFile(models.Model):
    generic_data_collection_data = models.ForeignKey(
        GenericDataCollectionData,
        on_delete=models.CASCADE,
        related_name="generic_data_collection_files",
    )
    file = models.FileField(upload_to=get_data_file_dir)


class MediaCollectionFile(models.Model):
    media_collection_data = models.ForeignKey(
        MediaCollectionData,
        on_delete=models.CASCADE,
        related_name="media_collection_files",
    )
    file = models.FileField(upload_to=get_data_file_dir)


class EEGElectrodePositionCollectionStatus(models.Model):
    eeg_data = models.ForeignKey(
        EEGData, on_delete=models.CASCADE, related_name="electrode_positions"
    )
    eeg_electrode_position_setting = models.ForeignKey(
        EEGElectrodePositionSetting, on_delete=models.CASCADE
    )
    worked = models.BooleanField()
    channel_index = models.IntegerField()

    class Meta:
        unique_together = ("eeg_data", "channel_index")

    def __str__(self) -> str:
        return self.eeg_electrode_position_setting.eeg_electrode_position.name


class GoalkeeperGame(models.Model):
    code = models.CharField(_("Code"), max_length=2, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class GoalkeeperPhase(models.Model):
    game = models.ForeignKey(GoalkeeperGame, on_delete=models.CASCADE)
    phase = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("game", "phase")

    def clean(self):
        if self.phase is None and GoalkeeperPhase.objects.filter(
            phase=self.phase, game=self.game
        ):
            raise ValidationError(_("Phase already registered"))

    def __str__(self) -> str:
        if self.phase:
            return _("{game} - phase {phase}").format(
                game=self.game.name, phase=self.phase
            )
        else:
            return self.game.name


class GoalkeeperGameLog(models.Model):
    file_content = models.TextField(primary_key=True, name="filecontent")

    class Meta:
        managed = False
        db_table = '"public"."results"'


class GoalkeeperGameConfig(models.Model):
    id_config = models.IntegerField(name="idconfig", primary_key=True)
    institution = models.CharField(name="institution", max_length=150)
    group_code = models.CharField(name="groupcode", max_length=150)
    soccer_team = models.CharField(name="soccerteam", max_length=150)
    game = models.CharField(name="game", max_length=2)
    phase = models.IntegerField(name="phase")
    player_alias = models.CharField(name="playeralias", max_length=20)
    sequence_executed = models.TextField(name="sequexecuted")
    date = models.CharField(name="gamedata", max_length=6)
    time = models.CharField(name="gametime", max_length=6)
    result_id = models.IntegerField(name="idresult")
    playid = models.TextField(name="playid", default="")
    sessiontime = models.FloatField(name="sessiontime", default="")
    relaxtime = models.FloatField(name="relaxtime", default="")
    playermachine = models.TextField(name="playermachine", default="")
    gamerandom = models.TextField(name="gamerandom", default="")
    limitplays = models.SmallIntegerField(name="limitplays", default="")
    totalcorrect = models.SmallIntegerField(name="totalcorrect", default="")
    successrate = models.FloatField(name="successrate", default="")
    gamemode = models.TextField(name="gamemode", default="")
    status = models.SmallIntegerField(name="status", default="")
    playstorelax = models.SmallIntegerField(name="playstorelax", default="")
    scoreboard = models.BooleanField(name="scoreboard", default="")
    finalscoreboard = models.SmallIntegerField(name="finalscoreboard", default="")
    animationtype = models.SmallIntegerField(name="animationtype", default="")
    minhits = models.SmallIntegerField(name="minhits", default="")

    class Meta:
        managed = settings.IS_TESTING
        db_table = '"public"."gameconfig"'


class GoalkeeperGameResults(models.Model):
    id = models.IntegerField(name="idgameresult", primary_key=True, default="")
    id_config = models.IntegerField(name="idconfig", default="")
    move = models.SmallIntegerField(name="move", default="")
    timeuntilanykey = models.FloatField(name="timeuntilanykey", default="")
    timeuntilshowagain = models.FloatField(name="timeuntilshowagain", default="")
    waitedresult = models.SmallIntegerField(name="waitedresult", default="")
    ehrandom = models.CharField(name="ehrandom", max_length=3, default="")
    optionchoosen = models.SmallIntegerField(name="optionchoosen", default="")
    movementtime = models.FloatField(name="movementtime", default="")
    decisiontime = models.FloatField(name="decisiontime", default="")

    class Meta:
        managed = settings.IS_TESTING
        db_table = '"public"."gameresults"'


class ScheduleOfSending(models.Model):
    SCHEDULE_STATUS_OPTIONS = (
        ("scheduled", _("scheduled")),
        ("canceled", _("canceled")),
        ("sending", _("sending")),
        ("sent", _("sent")),
        ("error_sending", _("error sending")),
    )
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="schedule_of_sending"
    )
    schedule_datetime = models.DateTimeField(auto_now_add=True)
    responsible = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=SCHEDULE_STATUS_OPTIONS)
    sending_datetime = models.DateTimeField(null=True)
    reason_for_resending = models.CharField(null=True, max_length=500)
    send_participant_age = models.BooleanField()


class PortalSelectedQuestion(models.Model):
    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, related_name="portal_selected_questions"
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question_code = models.CharField(max_length=150)

    class Meta:
        unique_together = ("experiment", "survey", "question_code")
