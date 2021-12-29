MODEL_ROOT_NODES = [
    "experiment.researchproject",
    "experiment.manufacturer",
    "survey.survey",
    "experiment.coilshape",
    "experiment.material",
    "experiment.electrodeconfiguration",
    "experiment.eegelectrodelocalizationsystem",
    "experiment.filtertype",
    "experiment.amplifierdetectiontype",
    "experiment.tetheringsystem",
    "experiment.muscle",
    "experiment.standardizationsystem",
    "experiment.brainareasystem",
    "patient.patient",
    "experiment.directionoftheinducedcurrent",
]

# Map ForeignKey relation fields between models.
# Models with relations:
# {
#   <app>.<model>: [(<app>.<related_model>, <foreignkey field>), [...]],
#   [...]
# }
# Models without relations:
# {
#   <app>.<model>: [('', '')]
FOREIGN_RELATIONS = {
    "experiment.researchproject": [("", "")],
    "experiment.experiment": [("experiment.researchproject", "research_project")],
    "experiment.group": [
        ("experiment.experiment", "experiment"),
        ("experiment.component", "experimental_protocol"),
    ],
    "experiment.component": [("experiment.experiment", "experiment")],
    "experiment.componentconfiguration": [
        ("experiment.component", "component"),
        ("experiment.component", "parent"),
    ],
    "experiment.questionnaire": [("survey.survey", "survey")],
    "survey.survey": [("", "")],
    "experiment.digitalgamephase": [
        ("experiment.contexttree", "context_tree"),
        ("experiment.softwareversion", "software_version"),
    ],
    "experiment.contexttree": [("experiment.experiment", "experiment")],
    # 'experiment.genericdatacollection': [('experiment.informationtype', 'information_type')],
    # 'experiment.informationtype': [('', '')],
    "experiment.stimulus": [("experiment.stimulustype", "stimulus_type")],
    "experiment.stimulustype": [("", "")],
    # TMS
    "experiment.tms": [("experiment.tmssetting", "tms_setting")],
    "experiment.tmssetting": [("experiment.experiment", "experiment")],
    "experiment.tmsdevicesetting": [
        ("experiment.coilmodel", "coil_model"),
        ("experiment.tmsdevice", "tms_device"),
    ],
    "experiment.coilmodel": [
        ("experiment.coilshape", "coil_shape"),
        ("experiment.material", "material"),
    ],
    "experiment.coilshape": [("", "")],
    "experiment.material": [("", "")],
    # EEG
    "experiment.eeg": [("experiment.eegsetting", "eeg_setting")],
    "experiment.eegsetting": [("experiment.experiment", "experiment")],
    "experiment.electrodemodel": [
        ("experiment.material", "material"),
        ("experiment.electrodeconfiguration", "electrode_configuration"),
    ],
    "experiment.eegelectrodepositionsetting": [
        ["experiment.electrodemodel", "electrode_model"],
        ["experiment.eegelectrodelayoutsetting", "eeg_electrode_layout_setting"],
        ["experiment.eegelectrodeposition", "eeg_electrode_position"],
    ],
    "experiment.eegelectrodelayoutsetting": [
        ("experiment.eegelectrodenetsystem", "eeg_electrode_net_system")
    ],
    "experiment.eegelectrodeposition": [
        (
            "experiment.eegelectrodelocalizationsystem",
            "eeg_electrode_localization_system",
        )
    ],
    "experiment.eegelectrodenetsystem": [
        (
            "experiment.eegelectrodelocalizationsystem",
            "eeg_electrode_localization_system",
        ),
        ("experiment.eegelectrodenet", "eeg_electrode_net"),
    ],
    "experiment.eegelectrodenet": [
        ("experiment.electrodemodel", "electrode_model_default")
    ],
    "experiment.eegcapsize": [("experiment.eegelectrodecap", "eeg_electrode_cap")],
    "experiment.eegfiltersetting": [("experiment.filtertype", "eeg_filter_type")],
    "experiment.eegamplifiersetting": [("experiment.amplifier", "eeg_amplifier")],
    "experiment.amplifier": [
        ("experiment.amplifierdetectiontype", "amplifier_detection_type"),
        ("experiment.tetheringsystem", "tethering_system"),
    ],
    "experiment.eegsolutionsetting": [("experiment.eegsolution", "eeg_solution")],
    "experiment.eegsolution": [("experiment.manufacturer", "manufacturer")],
    # EMG
    "experiment.emg": [("experiment.emgsetting", "emg_setting")],
    "experiment.emgsetting": [
        ("experiment.experiment", "experiment"),
        ("experiment.softwareversion", "acquisition_software_version"),
    ],
    "experiment.muscle": [("", "")],
    "experiment.standardizationsystem": [("", "")],
    "experiment.muscleside": [("experiment.muscle", "muscle")],
    "experiment.musclesubdivision": [("experiment.muscle", "muscle")],
    "experiment.emgelectrodeplacement": [
        ("experiment.musclesubdivision", "muscle_subdivision"),
        ("experiment.standardizationsystem", "standardization_system"),
    ],
    "experiment.emgelectrodesetting": [
        ("experiment.emgsetting", "emg_setting"),
        ("experiment.electrodemodel", "electrode"),
    ],
    "experiment.emgpreamplifiersetting": [("experiment.amplifier", "amplifier")],
    "experiment.emgelectrodeplacementsetting": [
        ("experiment.muscleside", "muscle_side"),
        ("experiment.emgelectrodeplacement", "emg_electrode_placement"),
    ],
    "experiment.softwareversion": [("experiment.software", "software")],
    "experiment.software": [("experiment.manufacturer", "manufacturer")],
    "experiment.manufacturer": [("", "")],
    "experiment.equipment": [("experiment.manufacturer", "manufacturer")],
    "experiment.emgadconvertersetting": [("experiment.adconverter", "ad_converter")],
    "experiment.emgdigitalfiltersetting": [("experiment.filtertype", "filter_type")],
    "experiment.filtertype": [("", "")],
    "experiment.tetheringsystem": [("", "")],
    "experiment.amplifierdetectiontype": [("", "")],
    "experiment.emgamplifiersetting": [("experiment.amplifier", "amplifier")],
    # Data collections
    "experiment.dataconfigurationtree": [
        ("experiment.componentconfiguration", "component_configuration"),
        ("experiment.dataconfigurationtree", "parent"),
    ],
    "experiment.eegdata": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.eegsetting", "eeg_setting"),
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.eegcapsize", "eeg_cap_size"),
    ],
    "experiment.eegfile": [("experiment.eegdata", "eeg_data")],
    "experiment.eegelectrodepositioncollectionstatus": [
        ("experiment.eegdata", "eeg_data"),
        ("experiment.eegelectrodepositionsetting", "eeg_electrode_position_setting"),
    ],
    "experiment.tmsdata": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.tmssetting", "tms_setting"),
        ("experiment.coilorientation", "coil_orientation"),
        ("experiment.directionoftheinducedcurrent", "direction_of_induced_current"),
    ],
    "experiment.directionoftheinducedcurrent": [("", "")],
    "experiment.coilorientation": [("", "")],
    "experiment.hotspot": [
        ("experiment.tmslocalizationsystem", "tms_localization_system")
    ],
    "experiment.tmslocalizationsystem": [("experiment.brainarea", "brain_area")],
    "experiment.brainarea": [("experiment.brainareasystem", "brain_area_system")],
    "experiment.brainareasystem": [("", "")],
    "experiment.additionaldatafile": [("experiment.additionaldata", "additional_data")],
    "experiment.fileformat": [
        ("", "")
    ],  # TODO (NES-965): see why this is not in MODEL_ROOT_NODES
    "experiment.additionaldata": [
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.fileformat", "file_format"),
    ],
    "experiment.digitalgamephasedata": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.fileformat", "file_format"),
    ],
    "experiment.digitalgamephasefile": [
        ("experiment.digitalgamephasedata", "digital_game_phase_data")
    ],
    "experiment.genericdatacollectiondata": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.fileformat", "file_format"),
    ],
    "experiment.genericdatacollectionfile": [
        ("experiment.genericdatacollectiondata", "generic_data_collection_data")
    ],
    "experiment.emgdata": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.subjectofgroup", "subject_of_group"),
        ("experiment.fileformat", "file_format"),
        ("experiment.emgsetting", "emg_setting"),
    ],
    "experiment.emgfile": [("experiment.emgdata", "emg_data")],
    "experiment.componentadditionalfile": [("experiment.component", "component")],
    "experiment.questionnaireresponse": [
        ("experiment.dataconfigurationtree", "data_configuration_tree"),
        ("experiment.subjectofgroup", "subject_of_group"),
    ],
    # Participants
    "experiment.subject": [("patient.patient", "patient")],
    "experiment.subjectofgroup": [
        ("experiment.subject", "subject"),
        ("experiment.group", "group"),
    ],
    "patient.patient": [("", "")],
    "patient.telephone": [("patient.patient", "patient")],
    "patient.socialdemographicdata": [("patient.patient", "patient")],
    "patient.socialhistorydata": [("patient.patient", "patient")],
    "patient.medicalrecorddata": [("patient.patient", "patient")],
    "patient.diagnosis": [("patient.medicalrecorddata", "medical_record_data")],
    "patient.complementaryexam": [("patient.diagnosis", "diagnosis")],
    "patient.examfile": [("patient.complementaryexam", "exam")],
}

# Map one to one relations between models (OneToOneFeild fields and multi-table inheritance).
# {
#   <app>.<model>: <app>.<model>
# }
ONE_TO_ONE_RELATION = {
    # Multi table inheritance
    "experiment.block": "experiment.component",
    "experiment.instruction": "experiment.component",
    "experiment.pause": "experiment.component",
    "experiment.questionnaire": "experiment.component",
    "experiment.stimulus": "experiment.component",
    "experiment.task": "experiment.component",
    "experiment.taskfortheexperimenter": "experiment.component",
    "experiment.eeg": "experiment.component",
    "experiment.emg": "experiment.component",
    "experiment.tms": "experiment.component",
    "experiment.digitalgamephase": "experiment.component",
    "experiment.genericdatacollection": "experiment.component",
    "experiment.tmsdevice": "experiment.equipment",
    "experiment.eegelectrodenet": "experiment.equipment",
    "experiment.eegelectrodecap": "experiment.eegelectrodenet",
    "experiment.amplifier": "experiment.equipment",
    "experiment.mriscanner": "experiment.equipment",
    "experiment.emgintramuscularplacement": "experiment.emgelectrodeplacement",
    "experiment.emgsurfaceplacement": "experiment.emgelectrodeplacement",
    "experiment.emgneedleplacement": "experiment.emgelectrodeplacement",
    "experiment.adconverter": "experiment.equipment",
    # OneToOneField
    "experiment.tmsdevicesetting": "experiment.tmssetting",
    "experiment.eegelectrodelayoutsetting": "experiment.eegsetting",
    "experiment.eegfiltersetting": "experiment.eegsetting",
    "experiment.eegamplifiersetting": "experiment.eegsetting",
    "experiment.eegsolutionsetting": "experiment.eegsetting",
    "experiment.emgadconvertersetting": "experiment.emgsetting",
    "experiment.emgdigitalfiltersetting": "experiment.emgsetting",
    "experiment.emgamplifiersetting": "experiment.emgelectrodesetting",
    "experiment.emganalogfiltersetting": "experiment.emgamplifiersetting",
    "experiment.emgpreamplifiersetting": "experiment.emgelectrodesetting",
    "experiment.emgpreamplifierfiltersetting": "experiment.emgpreamplifiersetting",
    "experiment.emgelectrodeplacementsetting": "experiment.emgelectrodesetting",
    "experiment.hotspot": "experiment.tmsdata",
}

# Define json file names (without extension) to map experiment related models.
# {
#   <filename>: (<model>, <experiment id path>),
#   [...]
# }
EXPERIMENT_JSON_FILES = {
    "experimentfixture": ("experiment", "id__in"),
    "componentconfiguration": (
        "componentconfiguration",
        "component_id__experiment_id__in",
    ),
    "dataconfigurationtree": (
        "dataconfigurationtree",
        "component_configuration__component__experiment_id__in",
    ),
    "eegdata": (
        "eegdata",
        "data_configuration_tree__component_configuration__component__experiment_id__in",
    ),
    "eegfile": (
        "eegfile",
        "eeg_data__data_configuration_tree__component_configuration__component__experiment_id__in",
    ),
    "eeg_electrodeposition_collection_status": (
        "eegelectrodepositioncollectionstatus",
        "eeg_data__data_configuration_tree__component_configuration__component__experiment_id__in",
    ),
    "group": ("group", "experiment_id__in"),
    "block": ("block", "component_ptr_id__experiment_id__in"),
    "instruction": ("instruction", "component_ptr_id__experiment_id__in"),
    "pause": ("pause", "component_ptr_id__experiment_id__in"),
    "questionnaire": ("questionnaire", "component_ptr_id__experiment_id__in"),
    "stimulus": ("stimulus", "component_ptr_id__experiment_id__in"),
    "task": ("task", "component_ptr_id__experiment_id__in"),
    "task_experiment": (
        "taskfortheexperimenter",
        "component_ptr_id__experiment_id__in",
    ),
    "eeg": ("eeg", "component_ptr_id__experiment_id__in"),
    "emg": ("emg", "component_ptr_id__experiment_id__in"),
    "tms": ("tms", "component_ptr_id__experiment_id__in"),
    "digital_game_phase": ("digitalgamephase", "component_ptr_id__experiment_id__in"),
    "generic_data_collection": (
        "genericdatacollection",
        "component_ptr_id__experiment_id__in",
    ),
    "participant": ("subjectofgroup", "group_id__experiment_id__in"),
    "tms_device": ("tmsdevicesetting", "tms_setting__experiment_id__in"),
    "tms_setting": ("tmssetting", "experiment_id__in"),
    "eeg_amplifier_setting": ("eegamplifiersetting", "eeg_setting__experiment_id__in"),
    "eeg_solution_setting": ("eegsolutionsetting", "eeg_setting__experiment_id__in"),
    "eeg_filter_setting": ("eegfiltersetting", "eeg_setting__experiment_id__in"),
    "eeg_electrode_layout_setting": (
        "eegelectrodelayoutsetting",
        "eeg_setting__experiment_id__in",
    ),
    "eeg_electrode_position_setting": (
        "eegelectrodepositionsetting",
        "eeg_electrode_layout_setting__eeg_setting__experiment_id__in",
    ),
    "eeg_setting": ("eegsetting", "experiment_id__in"),
    "emg_setting": ("emgsetting", "experiment_id__in"),
    "emg_ad_converter_setting": (
        "emgadconvertersetting",
        "emg_setting__experiment_id__in",
    ),
    "emg_digital_filter_setting": (
        "emgdigitalfiltersetting",
        "emg_setting__experiment_id__in",
    ),
    "emg_pre_amplifier_filter_setting": (
        "emgpreamplifierfiltersetting",
        "emg_preamplifier_filter_setting__emg_electrode_setting__emg_setting__experiment_id__in",
    ),
    "emg_amplifier_analog_filter_setting": (
        "emganalogfiltersetting",
        "emg_electrode_setting__emg_electrode_setting__emg_setting__experiment_id__in",
    ),
    "emg_electrodeplacementsetting": (
        "emgelectrodeplacementsetting",
        "emg_electrode_setting__emg_setting__experiment_id__in",
    ),
    "keywords": ("researchproject_keywords", "researchproject_id__in"),
    "tmsdata": ("tmsdata", "tms_setting__experiment_id__in"),
    "hotspot": ("hotspot", "tms_data__tms_setting__experiment_id__in"),
    "additionaldatafile": (
        "additionaldatafile",
        "additional_data__subject_of_group__group__experiment_id__in",
    ),
    "digitalgamephasefile": (
        "digitalgamephasefile",
        "digital_game_phase_data__subject_of_group__group__experiment_id__in",
    ),
    "genericdatacollectionfile": (
        "genericdatacollectionfile",
        "generic_data_collection_data__subject_of_group__group__experiment_id__in",
    ),
    "emgfile": ("emgfile", "emg_data__emg_setting__experiment_id__in"),
    "componentadditionalfile": (
        "componentadditionalfile",
        "component__experiment_id__in",
    ),
    "questionnaireresponse": (
        "questionnaireresponse",
        "data_configuration_tree__component_configuration__component__experiment_id__in",
    ),
}

# Define json file names (without extension) to map patient related models.
# {
#   <filename>: (<model>, <experiment id path>),
#   [...]
# }
PATIENT_JSON_FILES = {
    "telephone": (
        "telephone",
        "patient__subject__subjectofgroup__group__experiment_id__in",
    ),
    "socialhistorydata": (
        "socialhistorydata",
        "patient__subject__subjectofgroup__group__experiment_id__in",
    ),
    "socialdemographicdata": (
        "socialdemographicdata",
        "patient__subject__subjectofgroup__group__experiment_id__in",
    ),
    "diagnosis": (
        "diagnosis",
        "medical_record_data__patient__subject__subjectofgroup__group__experiment_id__in",
    ),
    "examfile": (
        "examfile",
        "exam__diagnosis__medical_record_data__patient__subject__subjectofgroup__group__experiment_id__in",
    ),
}

# Define json file names (without extension) that are not attached to an experiment through
# a chain of relational fields
# {
#   <filename>: (
#   <model> , <multi-table inheritade model pks>, <multi-table inheritade model>,
#   <json_filename already existent>),
#   ...
JSON_FILES_DETACHED_MODELS = {
    "emg_intramuscularplacement": (
        "emgintramuscularplacement",
        "emgelectrodeplacement_ptr__in",
        "experiment.emgelectrodeplacement",
        "emg_electrodeplacementsetting",
    ),
    "emg_surfaceplacement": (
        "emgsurfaceplacement",
        "emgelectrodeplacement_ptr__in",
        "experiment.emgelectrodeplacement",
        "emg_electrodeplacementsetting",
    ),
    "emg_needleplacement": (
        "emgneedleplacement",
        "emgelectrodeplacement_ptr__in",
        "experiment.emgelectrodeplacement",
        "emg_electrodeplacementsetting",
    ),
}

# Map ForeignKey fields for pre-loaded models.
# Dict key is a tupple with model and a tupple of fields the will be tested
# for equality when deciding if insert new model instance or not.
# Dict value is a list of tupples. Each tupple is formed by the model that relates
# to dict key model, and the field that points for to it.
# {
#   (<app>.<model>, (<field1>, <field2>, [...]): [(<app>.<model>, <ForeignKey field>), [...])]
# }
PRE_LOADED_MODELS_FOREIGN_KEYS = {
    ("experiment.manufacturer", ("name",)): [
        ("experiment.equipment", "manufacturer"),
        ("experiment.eegsolution", "manufacturer"),
        ("experiment.software", "manufacturer"),
    ],
    ("experiment.material", ("name", "description")): [
        ("experiment.electrodemodel", "material"),
        # Not used by the system (uncomment if it is)
        # ('experiment.intramuscularelectrode', 'insulation_material'),
        ("experiment.eegelectrodecap", "material"),
        ("experiment.coilmodel", "material"),
    ],
    ("experiment.muscle", ("name",)): [
        ("experiment.muscleside", "muscle"),
        ("experiment.musclesubdivision", "muscle"),
    ],
    (
        "experiment.musclesubdivision",
        ("name", "anatomy_origin", "anatomy_insertion", "anatomy_function"),
    ): [
        ("experiment.emgelectrodeplacement", "muscle_subdivision"),
    ],
    ("experiment.muscleside", ("name",)): [
        ("experiment.emgelectrodeplacementsetting", "muscle_side")
    ],
    ("experiment.filtertype", ("name", "description")): [
        ("experiment.emgdigitalfiltersetting", "filter_type"),
        ("experiment.eegfiltersetting", "eeg_filter_type"),
    ],
    (
        "experiment.electrodemodel",
        (
            "name",
            "description",
            "usability",
            "impedance",
            "impedance_unit",
            "inter_electrode_distance",
            "inter_electrode_distance_unit",
            "electrode_type",
        ),
    ): [
        ("experiment.emgelectrodesetting", "electrode"),
        ("experiment.eegelectrodenet", "electrode_model_default"),
        ("experiment.eegelectrodepositionsetting", "electrode_model"),
    ],
    (
        "experiment.amplifier",
        (
            "gain",
            "number_of_channels",
            "common_mode_rejection_ratio",
            "input_impedance",
            "input_impedance_unit",
        ),
    ): [
        ("experiment.emgamplifiersetting", "amplifier"),
        ("experiment.emgpreamplifiersetting", "amplifier"),
        ("experiment.eegamplifiersetting", "eeg_amplifier"),
    ],
    (
        "experiment.eegelectrodeposition",
        ("name", "coordinate_x", "coordinate_y", "channel_default_index"),
    ): [("experiment.eegelectrodepositionsetting", "eeg_electrode_position")],
    ("experiment.eegelectrodelocalizationsystem", ("name", "description")): [
        ("experiment.eegelectrodenetsystem", "eeg_electrode_localization_system"),
        ("experiment.eegelectrodeposition", "eeg_electrode_localization_system"),
    ],
    ("experiment.eegelectrodenet", ""): [
        ("experiment.eegelectrodenetsystem", "eeg_electrode_net")
    ],
    ("experiment.eegsolution", ("name", "components")): [
        ("experiment.eegsolutionsetting", "eeg_solution")
    ],
    (
        "experiment.emgsurfaceplacement",
        (
            "start_posture",
            "orientation",
            "fixation_on_the_skin",
            "reference_electrode",
            "clinical_test",
        ),
    ): [("experiment.emgelectrodeplacementsetting", "emg_electrode_placement")],
    ("experiment.standardizationsystem", ("name", "description")): [
        ("experiment.emgelectrodeplacement", "standardization_system")
    ],
}

# Map multi-table inheritance and fields of inheritade model
# {
#   <app>.<model>:  [<app>.<inheritade_model>, (<inheritade_model_field>, [...])
# }
PRE_LOADED_MODELS_INHERITANCE = {
    "experiment.amplifier": [
        "experiment.equipment",
        ("equipment_type", "identification", "description", "serial_number"),
    ],
    "experiment.eegelectrodenet": [
        "experiment.equipment",
        ("equipment_type", "identification", "description", "serial_number"),
    ],
    "experiment.emgsurfaceplacement": [
        "experiment.emgelectrodeplacement",
        ("location", "placement_type"),
    ],
}

# Map models pre-loaded using initial data from fixtures.
# Not editable models are considered with the same id
# presented in fixtures when importing. Therefore it's necessary to
# load fixtures before importing.
PRE_LOADED_MODELS_NOT_EDITABLE = [
    "experiment.eegelectrodenetsystem",
    "experiment.stimulustype",
    "experiment.tetheringsystem",
    "experiment.amplifierdetectiontype",
    "experiment.electrodeconfiguration",
    "experiment.coilshape",
    "experiment.eegelectrodecap",
    "experiment.fileformat",
]

# Maps multi-table inheritance
# {
#   <app>.<model>: (<first_model_inheritance>, <second_model_inheritance>, [...])
# }
PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE = {
    "experiment.eegelectrodecap": ("experiment.eegelectrodenet", "experiment.equipment")
}

# TODO: Éder: insert comment here!
PRE_LOADED_PATIENT_MODEL = {
    ("patient.patient", ("cpf", "name",)): [
        ("patient.socialhistorydata", "patient"),
        ("patient.medicalrecorddata", "patient"),
        ("patient.socialdemographicdata", "patient"),
        ("patient.telephone", "patient"),
        # TODO: patient.questionnaireresponse is not pre_loaded_model
        ("patient.questionnaireresponse", "patient"),
        ("experiment.subject", "patient"),
    ],
}

# Map models with FileField fields
#   {
#       <app>.<model>: <FileField field>,
#       ...
#   }
MODELS_WITH_FILE_FIELD = {
    "experiment.experiment": "ethics_committee_project_file",
    "experiment.eegelectrodelocalizationsystem": "map_image_file",
    "experiment.eegfile": "file",
    "experiment.tmslocalizationsystem": "tms_localization_system_image",
    "experiment.digitalgamephasefile": "file",
    "experiment.genericdatacollectionfile": "file",
    "experiment.additionaldatafile": "file",
    "experiment.componentadditionalfile": "file",
    "experiment.contexttree": "setting_file",
    "experiment.stimulus": "media_file",
    "patient.examfile": "content",
    "experiment.emgelectrodeplacement": "photo",
    "experiment.emgfile": "file",
}

# Map models that have a field pointing to auth.user table
#   [
#       (<app>.<model>, <field>),
#       ...
#   ]
MODELS_WITH_RELATION_TO_AUTH_USER = [
    ("patient.patient", "changed_by"),
    ("patient.telephone", "changed_by"),
    ("patient.medicalrecorddata", "record_responsible"),
    ("patient.socialdemographicdata", "changed_by"),
    ("patient.socialhistorydata", "changed_by"),
    ("experiment.researchproject", "owner"),
    ("experiment.questionnaireresponse", "questionnaire_responsible"),
]
