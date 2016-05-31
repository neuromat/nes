# -*- coding: UTF-8 -*-
import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from patient.models import Patient, ClassificationOfDiseases
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


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=150, blank=False)
    description = models.TextField(null=False, blank=False)
    research_project = models.ForeignKey(ResearchProject, null=False, blank=False)

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


class Manufacturer(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    EQUIPMENT_TYPES = (
        ("eeg_machine", _("EEG Machine")),
        ("eeg_amplifier", _("EEG Amplifier")),
        ("eeg_solution", _("EEG Solution")),
        ("eeg_filter", _("EEG Filter")),
        ("eeg_electrode_net", _("EEG Electrode Net"))
    )
    manufacturer = models.ForeignKey(Manufacturer, null=False, related_name="set_of_equipment")
    equipment_type = models.CharField(null=True, blank=True, max_length=50, choices=EQUIPMENT_TYPES)
    identification = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.identification

    class Meta:
        verbose_name = _('Equipment')
        verbose_name_plural = _('Equipment')


class EEGMachine(Equipment):
    number_of_channels = models.IntegerField(null=True, blank=True)
    software_version = models.CharField(max_length=150, null=True, blank=True)


class EEGAmplifier(Equipment):
    gain = models.FloatField(null=True, blank=True)


class EEGSolution(models.Model):
    name = models.CharField(max_length=150)
    components = models.TextField(null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, null=False, related_name="set_of_solution")


class EEGFilterType(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)


class Material(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)


class EEGElectrodeModel(models.Model):
    USABILITY_TYPES = (
        ("disposable", _("Disposable")),
        ("reusable", _("Reusable")),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    material = models.ForeignKey(Material, null=True, blank=True)
    usability = models.CharField(null=True, blank=True, max_length=50, choices=USABILITY_TYPES)
    impedance = models.FloatField(null=True, blank=True)
    impedance_unit = models.CharField(null=True, blank=True, max_length=15, choices=IMPEDANCE_UNIT)


class EEGElectrodeNet(Equipment):
    electrode_model_default = models.ForeignKey(EEGElectrodeModel)

    def __str__(self):
        return self.identification


class EEGElectrodeCap(EEGElectrodeNet):
    material = models.ForeignKey(Material, null=True, blank=True)


class EEGCapSize(models.Model):
    eeg_electrode_cap = models.ForeignKey(EEGElectrodeCap)
    size = models.CharField(max_length=30)
    electrode_adjacent_distance = models.FloatField(null=True, blank=True)


def get_eeg_electrode_system_dir(instance, filename):
    return "eeg_electrode_system_files/%s/%s" % \
           (instance.id, filename)


class EEGElectrodeLocalizationSystem(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    number_of_electrodes = models.IntegerField(null=True, blank=True)
    map_image_file = models.FileField(upload_to=get_eeg_electrode_system_dir, null=True, blank=True)

    def __str__(self):
        return self.name


class EEGElectrodePosition(models.Model):
    eeg_electrode_localization_system = models.ForeignKey(EEGElectrodeLocalizationSystem)
    name = models.CharField(max_length=150)
    coordinate_x = models.IntegerField(null=True, blank=True)
    coordinate_y = models.IntegerField(null=True, blank=True)
    position_reference = models.ForeignKey('self', null=True, related_name='children')


class EEGElectrodeNetSystem(models.Model):
    eeg_electrode_net = models.ForeignKey(EEGElectrodeNet, related_name="set_of_electrode_net_system")
    eeg_electrode_localization_system = models.ForeignKey(EEGElectrodeLocalizationSystem,
                                                          related_name='set_of_electrode_net_system')


class EEGSetting(models.Model):
    experiment = models.ForeignKey(Experiment)
    name = models.CharField(max_length=150)
    description = models.TextField()
    copied_from = models.ForeignKey('self', null=True, related_name='children')
    # set_of_equipment = models.ManyToManyField(Equipment)

    def __str__(self):
        return self.name


class EEGMachineSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_machine_setting')
    eeg_machine = models.ForeignKey(EEGMachine)
    number_of_channels_used = models.IntegerField()


class EEGAmplifierSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_amplifier_setting')
    eeg_amplifier = models.ForeignKey(EEGAmplifier)
    gain = models.FloatField(null=True, blank=True)


class EEGSolutionSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_solution_setting')
    eeg_solution = models.ForeignKey(EEGSolution)


class EEGFilterSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_filter_setting')
    eeg_filter_type = models.ForeignKey(EEGFilterType)
    high_pass = models.FloatField(null=True, blank=True)
    low_pass = models.FloatField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)


class EEGElectrodeLayoutSetting(models.Model):
    eeg_setting = models.OneToOneField(EEGSetting, primary_key=True, related_name='eeg_electrode_layout_setting')
    eeg_electrode_net_system = models.ForeignKey(EEGElectrodeNetSystem)
    number_of_electrodes = models.IntegerField()


class EEGElectrodePositionSetting(models.Model):
    eeg_electrode_layout_setting = models.ForeignKey(EEGElectrodeLayoutSetting)
    eeg_electrode_position = models.ForeignKey(EEGElectrodePosition)
    used = models.BooleanField()


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
    )

    identification = models.CharField(null=False, max_length=50, blank=False)
    description = models.TextField(null=True, blank=True)
    duration_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    duration_unit = models.CharField(null=True, blank=True, max_length=15, choices=TIME_UNITS)
    experiment = models.ForeignKey(Experiment, null=False)
    component_type = models.CharField(null=False, max_length=15, choices=COMPONENT_TYPES)


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


class Stimulus(Component):
    stimulus_type = models.ForeignKey(StimulusType, null=False, blank=False)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Questionnaire(Component):
    survey = models.ForeignKey(Survey, null=False, blank=False, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class Block(Component):
    SEQUENCE = 'sequence'
    PARALLEL_BLOCK = 'parallel_block'
    number_of_mandatory_components = models.IntegerField(null=True, blank=True)
    type = models.CharField(null=False, max_length=20,
                            choices=((SEQUENCE, "Sequence component"),
                                     (PARALLEL_BLOCK, "Parallel block component")))

    def save(self, *args, **kwargs):
        super(Component, self).save(*args, **kwargs)


class EEG(Component):
    eeg_setting = models.ForeignKey(EEGSetting)

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

    class Meta:
        unique_together = ('parent', 'order',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
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


class SubjectOfGroup(models.Model):
    subject = models.ForeignKey(Subject, null=False, blank=False)
    group = models.ForeignKey(Group, null=False, blank=False)
    consent_form = models.FileField(upload_to=get_dir, null=True)

    class Meta:
        unique_together = ('subject', 'group',)


class DataConfigurationTree(models.Model):
    component_configuration = models.ForeignKey(ComponentConfiguration, on_delete=models.PROTECT)
    parent = models.ForeignKey('self', null=True, related_name='children')


class DataCollection(models.Model):
    data_configuration_tree = models.ForeignKey(DataConfigurationTree)
    subject_of_group = models.ForeignKey(SubjectOfGroup)
    date = models.DateField(default=datetime.date.today, null=False,
                            validators=[validate_date_questionnaire_response])

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

    def __str__(self):
        return self.name


class DataFile(models.Model):
    description = models.TextField(null=False, blank=False)
    file = models.FileField(upload_to=get_eeg_dir, null=False)
    file_format = models.ForeignKey(FileFormat, null=False, blank=False)
    file_format_description = models.TextField(null=True, blank=True, default='')

    class Meta:
        abstract = True


class EEGData(DataFile, DataCollection):
    eeg_setting = models.ForeignKey(EEGSetting)
    eeg_setting_reason_for_change = models.TextField(null=True, blank=True, default='')
    eeg_cap_size = models.ForeignKey(EEGCapSize, null=True)


class EEGElectrodePositionCollectionStatus(models.Model):
    eeg_data = models.ForeignKey(EEGData)
    eeg_electrode_position_setting = models.ForeignKey(EEGElectrodePositionSetting)
    worked = models.BooleanField()
