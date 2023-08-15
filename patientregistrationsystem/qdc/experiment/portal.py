import os
from csv import reader
from datetime import date, timedelta
from io import StringIO
from os import path

import coreapi
from django.conf import settings
from django.utils import translation
from survey.abc_search_engine import Questionnaires
from survey.survey_utils import QuestionnaireUtils
from survey.views import questionnaire_evaluation_fields_excluded

from .models import (
    EEG,
    EMG,
    TMS,
    ADConverter,
    AdditionalData,
    Amplifier,
    Block,
    CoilModel,
    ComponentConfiguration,
    ContextTree,
    DigitalGamePhase,
    DigitalGamePhaseData,
    EEGAmplifierSetting,
    EEGData,
    EEGElectrodeLocalizationSystem,
    EEGElectrodeNet,
    EEGElectrodePositionSetting,
    EEGFilterSetting,
    EEGSetting,
    EEGSolutionSetting,
    ElectrodeModel,
    EMGADConverterSetting,
    EMGAmplifierSetting,
    EMGAnalogFilterSetting,
    EMGData,
    EMGDigitalFilterSetting,
    EMGElectrodePlacementSetting,
    EMGElectrodeSetting,
    EMGIntramuscularPlacement,
    EMGNeedlePlacement,
    EMGPreamplifierFilterSetting,
    EMGPreamplifierSetting,
    EMGSetting,
    EMGSurfacePlacement,
    Experiment,
    ExperimentResearcher,
    GenericDataCollection,
    GenericDataCollectionData,
    Group,
    Instruction,
    IntramuscularElectrode,
    NeedleElectrode,
    Questionnaire,
    QuestionnaireResponse,
    Stimulus,
    Subject,
    SurfaceElectrode,
    TMSData,
    TMSDevice,
    TMSDeviceSetting,
    TMSSetting,
    User,
)


class RestApiClient(object):
    client = None
    schema = None
    active = False

    def __init__(self):
        auth = coreapi.auth.BasicAuthentication(
            username=settings.PORTAL_API["USER"],
            password=settings.PORTAL_API["PASSWORD"],
        )
        self.client = coreapi.Client(auth=auth)

        try:
            url = (
                settings.PORTAL_API["URL"]
                + (
                    ":" + settings.PORTAL_API["PORT"]
                    if settings.PORTAL_API["PORT"]
                    else ""
                )
                + "/api/schema/"
            )

            self.schema = self.client.get(url)
            self.active = True
        except:
            self.active = False


def get_portal_status():
    return RestApiClient().active


def send_experiment_to_portal(experiment: Experiment):
    """
    :param experiment: Experiment model instance
    :return: coreapi.Client().action returning entity
    """
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "nes_id": str(experiment.id),
        "title": experiment.title,
        "description": experiment.description,
        "data_acquisition_done": str(experiment.data_acquisition_is_concluded),
        "project_url": experiment.source_code_url,
        "ethics_committee_url": experiment.ethics_committee_project_url,
        "release_notes": experiment.schedule_of_sending.get(
            status="scheduled"
        ).reason_for_resending,
    }

    action_keys = ["experiments", "create"]

    if experiment.ethics_committee_project_file:
        with open(
            path.join(
                settings.MEDIA_ROOT, experiment.ethics_committee_project_file.name
            ),
            "rb",
        ) as f:
            params["ethics_committee_file"] = coreapi.utils.File(
                os.path.basename(experiment.ethics_committee_project_file.name), f
            )

            portal_experiment = rest.client.action(
                rest.schema, action_keys, params=params, encoding="multipart/form-data"
            )
    else:
        portal_experiment = rest.client.action(
            rest.schema, action_keys, params=params, encoding="multipart/form-data"
        )

    return portal_experiment


def send_experiment_end_message_to_portal(experiment: Experiment):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(experiment.id),
        "nes_id": str(experiment.id),
        "status": "to_be_analysed",
        "title": experiment.title,
        "description": experiment.description,
    }

    action_keys = ["experiments", "update"]

    portal_experiment = rest.client.action(rest.schema, action_keys, params=params)

    return portal_experiment


def send_group_to_portal(group: Group):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(group.experiment.id),
        "title": group.title,
        "description": group.description,
        "inclusion_criteria": [],
    }

    for criteria in group.classification_of_diseases.all():
        params["inclusion_criteria"].append({"code": criteria.code})

    action_keys = ["experiments", "groups", "create"]

    portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_publication_to_portal(publication, experiment_id):
    # if publication is not associated with Experiment.objects.get(
    # pk=experiment_id), generate exception DoesNotExist
    publication.experiments.get(pk=experiment_id)

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_id),
        "title": publication.title,
        "citation": publication.citation,
        "url": publication.url,
    }
    action_keys = ["experiments", "publications", "create"]
    portal_publications = rest.client.action(rest.schema, action_keys, params=params)

    return portal_publications


def send_experimental_protocol_to_portal(
    portal_group_id, textual_description, image, root_step_id
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {"id": portal_group_id}

    if textual_description:
        params["textual_description"] = textual_description

    if root_step_id:
        params["root_step"] = root_step_id

    action_keys = ["groups", "experimental_protocol", "create"]

    if image:
        with open(settings.BASE_DIR + image, "rb") as f:
            params["image"] = coreapi.utils.File(os.path.basename(image), f)
            portal_experimental_protocol = rest.client.action(
                rest.schema, action_keys, params=params, encoding="multipart/form-data"
            )
    else:
        portal_experimental_protocol = rest.client.action(
            rest.schema, action_keys, params=params
        )

    return portal_experimental_protocol


def send_eeg_setting_to_portal(eeg_setting: EEGSetting):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(eeg_setting.experiment_id),
        "name": eeg_setting.name,
        "description": eeg_setting.description,
    }

    action_keys = ["experiments", "eeg_setting", "create"]

    portal_eeg_setting = rest.client.action(rest.schema, action_keys, params=params)

    # amplifier setting
    if hasattr(eeg_setting, "eeg_amplifier_setting"):
        portal_amplifier = send_amplifier_to_portal(
            eeg_setting.experiment_id, eeg_setting.eeg_amplifier_setting.eeg_amplifier
        )
        eeg_amplifier_setting = send_eeg_amplifier_setting_to_portal(
            portal_eeg_setting["id"],
            portal_amplifier["id"],
            eeg_setting.eeg_amplifier_setting,
        )

    # solution setting
    if hasattr(eeg_setting, "eeg_solution_setting"):
        eeg_solution_setting = send_eeg_solution_setting_to_portal(
            portal_eeg_setting["id"], eeg_setting.eeg_solution_setting
        )

    # filter setting
    if hasattr(eeg_setting, "eeg_filter_setting"):
        eeg_filter_setting = send_eeg_filter_setting_to_portal(
            portal_eeg_setting["id"], eeg_setting.eeg_filter_setting
        )

    # electrode layout setting
    if hasattr(eeg_setting, "eeg_electrode_layout_setting"):
        # electrode net
        eeg_electrode_net_setting = send_eeg_electrode_net_setting_to_portal(
            portal_eeg_setting["id"],
            eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net,
        )

        electrode_models = {}
        localization_system = (
            eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_localization_system
        )

        # electrode localization system
        localization_system_portal = send_eeg_electrode_localization_system_to_portal(
            portal_eeg_setting["id"], localization_system
        )

        for (
            position
        ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
            if position.used:
                # electrode model
                if position.electrode_model.id not in electrode_models:
                    electrode_model_portal = send_electrode_model_to_portal(
                        eeg_setting.experiment_id, position.electrode_model
                    )
                    electrode_models[
                        position.electrode_model.id
                    ] = electrode_model_portal
                else:
                    electrode_model_portal = electrode_models[
                        position.electrode_model.id
                    ]

                # electrode position
                electrode_position_portal = send_eeg_electrode_position_to_portal(
                    portal_eeg_setting["id"], electrode_model_portal["id"], position
                )

    return portal_eeg_setting


def send_amplifier_to_portal(experiment_nes_id, amplifier: Amplifier):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "manufacturer_name": amplifier.manufacturer.name,
        "equipment_type": amplifier.equipment_type,
        "identification": amplifier.identification,
        "description": amplifier.description,
        "serial_number": amplifier.serial_number,
        "gain": amplifier.gain,
        "number_of_channels": amplifier.number_of_channels,
        "common_mode_rejection_ratio": amplifier.common_mode_rejection_ratio,
        "input_impedance": amplifier.input_impedance,
        "input_impedance_unit": amplifier.input_impedance_unit,
        "amplifier_detection_type_name": amplifier.amplifier_detection_type.name
        if amplifier.amplifier_detection_type
        else None,
        "tethering_system_name": amplifier.tethering_system.name
        if amplifier.tethering_system
        else None,
    }

    action_keys = ["experiments", "amplifier", "create"]

    portal_amplifier = rest.client.action(rest.schema, action_keys, params=params)

    return portal_amplifier


def send_eeg_amplifier_setting_to_portal(
    portal_eeg_setting_id,
    portal_amplifier_id,
    eeg_amplifier_setting: EEGAmplifierSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "eeg_amplifier": portal_amplifier_id,
        "gain": eeg_amplifier_setting.gain,
        "sampling_rate": eeg_amplifier_setting.sampling_rate,
        "number_of_channels_used": eeg_amplifier_setting.number_of_channels_used,
    }

    action_keys = ["eeg_setting", "eeg_amplifier_setting", "create"]

    portal_eeg_amplifier_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_eeg_amplifier_setting


def send_eeg_solution_setting_to_portal(
    portal_eeg_setting_id, eeg_solution_setting: EEGSolutionSetting
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "manufacturer_name": eeg_solution_setting.eeg_solution.manufacturer.name,
        "name": eeg_solution_setting.eeg_solution.name,
        "components": eeg_solution_setting.eeg_solution.components,
    }

    action_keys = ["eeg_setting", "eeg_solution_setting", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_eeg_filter_setting_to_portal(
    portal_eeg_setting_id, eeg_filter_setting: EEGFilterSetting
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "eeg_filter_type_name": eeg_filter_setting.eeg_filter_type.name,
        "eeg_filter_type_description": eeg_filter_setting.eeg_filter_type.description,
        "high_pass": eeg_filter_setting.high_pass,
        "low_pass": eeg_filter_setting.low_pass,
        "high_band_pass": eeg_filter_setting.high_band_pass,
        "low_band_pass": eeg_filter_setting.low_band_pass,
        "high_notch": eeg_filter_setting.high_notch,
        "low_notch": eeg_filter_setting.low_notch,
        "order": eeg_filter_setting.order,
    }

    action_keys = ["eeg_setting", "eeg_filter_setting", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_eeg_electrode_net_setting_to_portal(
    portal_eeg_setting_id, eeg_electrode_net: EEGElectrodeNet
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "manufacturer_name": eeg_electrode_net.manufacturer.name,
        "equipment_type": eeg_electrode_net.equipment_type,
        "identification": eeg_electrode_net.identification,
        "description": eeg_electrode_net.description,
        "serial_number": eeg_electrode_net.serial_number,
    }

    action_keys = ["eeg_setting", "eeg_electrode_net_setting", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_eeg_electrode_localization_system_to_portal(
    portal_eeg_setting_id,
    eeg_electrode_localization_system: EEGElectrodeLocalizationSystem,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "name": eeg_electrode_localization_system.name,
        "description": eeg_electrode_localization_system.description,
    }

    if eeg_electrode_localization_system.map_image_file:
        map_image_file = open(
            path.join(
                settings.MEDIA_ROOT,
                eeg_electrode_localization_system.map_image_file.name,
            ),
            "rb",
        )
        params["map_image_file"] = coreapi.utils.File(
            os.path.basename(eeg_electrode_localization_system.map_image_file.name),
            map_image_file,
        )

    action_keys = ["eeg_setting", "eeg_electrode_localization_system", "create"]

    portal_participant = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return portal_participant


def send_eeg_electrode_position_to_portal(
    portal_eeg_setting_id,
    portal_electrode_model_id,
    eeg_electrode_position_setting: EEGElectrodePositionSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_eeg_setting_id,
        "electrode_model": portal_electrode_model_id,
        "name": eeg_electrode_position_setting.eeg_electrode_position.name,
        "coordinate_x": eeg_electrode_position_setting.eeg_electrode_position.coordinate_x,
        "coordinate_y": eeg_electrode_position_setting.eeg_electrode_position.coordinate_y,
        "channel_index": eeg_electrode_position_setting.channel_index,
    }

    action_keys = ["eeg_setting", "eeg_electrode_position", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_electrode_model_to_portal(experiment_nes_id, electrode_model: ElectrodeModel):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "name": electrode_model.name,
        "description": electrode_model.description,
        "material": electrode_model.material.name,
        "usability": electrode_model.usability,
        "impedance": electrode_model.impedance,
        "impedance_unit": electrode_model.impedance_unit,
        "inter_electrode_distance": electrode_model.inter_electrode_distance,
        "inter_electrode_distance_unit": electrode_model.inter_electrode_distance_unit,
        "electrode_configuration_name": electrode_model.electrode_configuration.name
        if electrode_model.electrode_configuration
        else None,
        "electrode_type": electrode_model.electrode_type,
    }

    if electrode_model.electrode_type == "surface":
        action_keys = ["experiments", "surface_electrode", "create"]
        electrode_instance = SurfaceElectrode.objects.filter(id=electrode_model.id)
        if electrode_instance:
            electrode_instance = electrode_instance[0]
            params["conduction_type"] = electrode_instance.conduction_type
            params["electrode_mode"] = electrode_instance.electrode_mode
            params["electrode_shape_name"] = electrode_instance.electrode_shape.name
            if electrode_instance.electrodesurfacemeasure_set:
                params[
                    "electrode_shape_measure_value"
                ] = electrode_instance.electrodesurfacemeasure_set.first().value
                params[
                    "electrode_shape_measure_unit"
                ] = (
                    electrode_instance.electrodesurfacemeasure_set.first().measure_unit.name
                )

    elif electrode_model.electrode_type == "needle":
        action_keys = ["experiments", "needle_electrode", "create"]
        electrode_instance = NeedleElectrode.objects.get(pk=electrode_model.id)
        params["size"] = electrode_instance.size
        params["size_unit"] = electrode_instance.size_unit
        params[
            "number_of_conductive_contact_points_at_the_tip"
        ] = electrode_instance.number_of_conductive_contact_points_at_the_tip
        params[
            "size_of_conductive_contact_points_at_the_tip"
        ] = electrode_instance.size_of_conductive_contact_points_at_the_tip

    else:
        action_keys = ["experiments", "intramuscular_electrode", "create"]
        electrode_instance = IntramuscularElectrode.objects.get(pk=electrode_model.id)
        params["strand"] = electrode_instance.strand
        params["insulation_material_name"] = (
            electrode_instance.insulation_material.name
            if electrode_instance.insulation_material
            else None
        )
        params["insulation_material_description"] = (
            electrode_instance.insulation_material.description
            if electrode_instance.insulation_material
            else None
        )
        params["length_of_exposed_tip"] = electrode_instance.length_of_exposed_tip

    portal_instance = rest.client.action(rest.schema, action_keys, params=params)

    return portal_instance


def send_emg_digital_filter_setting_to_portal(
    portal_emg_setting_id, emg_digital_filter_setting: EMGDigitalFilterSetting
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_setting_id,
        "filter_type_name": emg_digital_filter_setting.filter_type.name,
        "filter_type_description": emg_digital_filter_setting.filter_type.description,
        "low_pass": emg_digital_filter_setting.low_pass,
        "high_pass": emg_digital_filter_setting.high_pass,
        "low_band_pass": emg_digital_filter_setting.low_band_pass,
        "high_band_pass": emg_digital_filter_setting.high_band_pass,
        "low_notch": emg_digital_filter_setting.low_notch,
        "high_notch": emg_digital_filter_setting.high_notch,
        "order": emg_digital_filter_setting.order,
    }

    action_keys = ["emg_setting", "emg_digital_filter_setting", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_ad_converter_to_portal(experiment_nes_id, ad_converter: ADConverter):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "manufacturer_name": ad_converter.manufacturer.name,
        "equipment_type": ad_converter.equipment_type,
        "identification": ad_converter.identification,
        "description": ad_converter.description,
        "serial_number": ad_converter.serial_number,
        "signal_to_noise_rate": ad_converter.signal_to_noise_rate,
        "sampling_rate": ad_converter.sampling_rate,
        "resolution": ad_converter.resolution,
    }

    action_keys = ["experiments", "ad_converter", "create"]

    portal_ad_converter = rest.client.action(rest.schema, action_keys, params=params)

    return portal_ad_converter


def send_emg_ad_converter_setting_to_portal(
    portal_emg_setting_id,
    portal_ad_converter_id,
    emg_ad_converter_setting: EMGADConverterSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_setting_id,
        "ad_converter": portal_ad_converter_id,
        "sampling_rate": emg_ad_converter_setting.sampling_rate,
    }

    action_keys = ["emg_setting", "emg_ad_converter_setting", "create"]

    portal_ad_converter_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_ad_converter_setting


def send_emg_electrode_setting_to_portal(
    portal_emg_setting_id,
    portal_electrode_model_id,
    emg_electrode_setting: EMGElectrodeSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {"id": portal_emg_setting_id, "electrode_model": portal_electrode_model_id}

    action_keys = ["emg_setting", "emg_electrode_setting", "create"]

    portal_electrode_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_electrode_setting


def send_emg_preamplifier_setting_to_portal(
    portal_emg_electrode_setting_id,
    portal_preamplifier_id,
    emg_preamplifier_setting: EMGPreamplifierSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_electrode_setting_id,
        "amplifier": portal_preamplifier_id,
        "gain": emg_preamplifier_setting.gain,
    }

    action_keys = ["emg_electrode_setting", "emg_preamplifier_setting", "create"]

    portal_preamplifier_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_preamplifier_setting


def send_emg_amplifier_setting_to_portal(
    portal_emg_electrode_setting_id,
    portal_amplifier_id,
    emg_amplifier_setting: EMGAmplifierSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_electrode_setting_id,
        "amplifier": portal_amplifier_id,
        "gain": emg_amplifier_setting.gain,
    }

    action_keys = ["emg_electrode_setting", "emg_amplifier_setting", "create"]

    portal_amplifier_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_amplifier_setting


def send_emg_preamplifier_filter_setting_to_portal(
    portal_emg_electrode_setting_id,
    emg_preamplifier_filter_setting: EMGPreamplifierFilterSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_electrode_setting_id,
        "low_pass": emg_preamplifier_filter_setting.low_pass,
        "high_pass": emg_preamplifier_filter_setting.high_pass,
        "low_band_pass": emg_preamplifier_filter_setting.low_band_pass,
        "low_notch": emg_preamplifier_filter_setting.low_notch,
        "high_band_pass": emg_preamplifier_filter_setting.high_band_pass,
        "high_notch": emg_preamplifier_filter_setting.high_notch,
        "order": emg_preamplifier_filter_setting.order,
    }

    action_keys = ["emg_electrode_setting", "emg_preamplifier_filter_setting", "create"]

    portal_preamplifier_filter_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_preamplifier_filter_setting


def send_emg_analog_filter_setting_to_portal(
    portal_emg_electrode_setting_id, emg_analog_filter_setting: EMGAnalogFilterSetting
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_electrode_setting_id,
        "low_pass": emg_analog_filter_setting.low_pass,
        "high_pass": emg_analog_filter_setting.high_pass,
        "low_band_pass": emg_analog_filter_setting.low_band_pass,
        "low_notch": emg_analog_filter_setting.low_notch,
        "high_band_pass": emg_analog_filter_setting.high_band_pass,
        "high_notch": emg_analog_filter_setting.high_notch,
        "order": emg_analog_filter_setting.order,
    }

    action_keys = ["emg_electrode_setting", "emg_analog_filter_setting", "create"]

    portal_preamplifier_filter_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_preamplifier_filter_setting


def send_emg_surface_placement_to_portal(
    experiment_nes_id, emg_surface_placement: EMGSurfacePlacement
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "standardization_system_name": emg_surface_placement.standardization_system.name,
        "standardization_system_description": emg_surface_placement.standardization_system.description,
        "muscle_anatomy_origin": emg_surface_placement.muscle_subdivision.anatomy_origin,
        "muscle_anatomy_insertion": emg_surface_placement.muscle_subdivision.anatomy_insertion,
        "muscle_anatomy_function": emg_surface_placement.muscle_subdivision.anatomy_function,
        "location": emg_surface_placement.location,
        "placement_type": emg_surface_placement.placement_type,
        "start_posture": emg_surface_placement.start_posture,
        "orientation": emg_surface_placement.orientation,
        "fixation_on_the_skin": emg_surface_placement.fixation_on_the_skin,
        "reference_electrode": emg_surface_placement.reference_electrode,
        "clinical_test": emg_surface_placement.clinical_test,
    }

    if emg_surface_placement.photo:
        photo_file = open(
            path.join(settings.MEDIA_ROOT, emg_surface_placement.photo.name), "rb"
        )
        params["photo"] = coreapi.utils.File(
            os.path.basename(emg_surface_placement.photo.name), photo_file
        )

    action_keys = ["experiments", "emg_surface_placement", "create"]

    portal_surface_placement = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return portal_surface_placement


def send_emg_intramuscular_placement_to_portal(
    experiment_nes_id, emg_intramuscular_placement: EMGIntramuscularPlacement
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "standardization_system_name": emg_intramuscular_placement.standardization_system.name,
        "standardization_system_description": emg_intramuscular_placement.standardization_system.description,
        "muscle_anatomy_origin": emg_intramuscular_placement.muscle_subdivision.anatomy_origin,
        "muscle_anatomy_insertion": emg_intramuscular_placement.muscle_subdivision.anatomy_insertion,
        "muscle_anatomy_function": emg_intramuscular_placement.muscle_subdivision.anatomy_function,
        "location": emg_intramuscular_placement.location,
        "placement_type": emg_intramuscular_placement.placement_type,
        "method_of_insertion": emg_intramuscular_placement.method_of_insertion,
        "depth_of_insertion": emg_intramuscular_placement.depth_of_insertion,
    }

    if emg_intramuscular_placement.photo:
        photo_file = open(
            path.join(settings.MEDIA_ROOT, emg_intramuscular_placement.photo.name), "rb"
        )
        params["photo"] = coreapi.utils.File(
            os.path.basename(emg_intramuscular_placement.photo.name), photo_file
        )

    action_keys = ["experiments", "emg_intramuscular_placement", "create"]

    portal_intramuscular_placement = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return portal_intramuscular_placement


def send_emg_needle_placement_to_portal(
    experiment_nes_id, emg_needle_placement: EMGNeedlePlacement
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "standardization_system_name": emg_needle_placement.standardization_system.name,
        "standardization_system_description": emg_needle_placement.standardization_system.description,
        "muscle_anatomy_origin": emg_needle_placement.muscle_subdivision.anatomy_origin,
        "muscle_anatomy_insertion": emg_needle_placement.muscle_subdivision.anatomy_insertion,
        "muscle_anatomy_function": emg_needle_placement.muscle_subdivision.anatomy_function,
        "location": emg_needle_placement.location,
        "placement_type": emg_needle_placement.placement_type,
        "depth_of_insertion": emg_needle_placement.depth_of_insertion,
    }

    if emg_needle_placement.photo:
        photo_file = open(
            path.join(settings.MEDIA_ROOT, emg_needle_placement.photo.name), "rb"
        )
        params["photo"] = coreapi.utils.File(
            os.path.basename(emg_needle_placement.photo.name), photo_file
        )

    action_keys = ["experiments", "emg_needle_placement", "create"]

    portal_needle_placement = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return portal_needle_placement


def send_emg_electrode_placement_setting_to_portal(
    portal_emg_electrode_setting_id,
    portal_electrode_placement_id,
    emg_electrode_placement_setting: EMGElectrodePlacementSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_emg_electrode_setting_id,
        "emg_electrode_placement": portal_electrode_placement_id,
        "muscle_side": emg_electrode_placement_setting.muscle_side.name
        if emg_electrode_placement_setting.muscle_side
        else None,
        "muscle_name": emg_electrode_placement_setting.muscle_side.muscle.name
        if emg_electrode_placement_setting.muscle_side
        else None,
        "remarks": emg_electrode_placement_setting.remarks,
    }

    action_keys = ["emg_electrode_setting", "emg_electrode_placement_setting", "create"]

    portal_preamplifier_setting = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_preamplifier_setting


def send_emg_setting_to_portal(emg_setting: EMGSetting):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(emg_setting.experiment_id),
        "name": emg_setting.name,
        "description": emg_setting.description,
        "acquisition_software_version": emg_setting.acquisition_software_version.software.name
        + " "
        + emg_setting.acquisition_software_version.name,
    }

    action_keys = ["experiments", "emg_setting", "create"]

    portal_emg_setting = rest.client.action(rest.schema, action_keys, params=params)

    # digital filter setting
    if hasattr(emg_setting, "emg_digital_filter_setting"):
        emg_digital_filter_setting = send_emg_digital_filter_setting_to_portal(
            portal_emg_setting["id"], emg_setting.emg_digital_filter_setting
        )

    # ad converter setting
    if hasattr(emg_setting, "emg_ad_converter_setting"):
        portal_ad_converter = send_ad_converter_to_portal(
            emg_setting.experiment_id, emg_setting.emg_ad_converter_setting.ad_converter
        )
        emg_ad_converter_setting = send_emg_ad_converter_setting_to_portal(
            portal_emg_setting["id"],
            portal_ad_converter["id"],
            emg_setting.emg_ad_converter_setting,
        )

    electrode_models = {}

    # electrode settings
    for emg_electrode_setting in emg_setting.emg_electrode_settings.all():
        # electrode model
        if emg_electrode_setting.electrode.id not in electrode_models:
            electrode_model_portal = send_electrode_model_to_portal(
                emg_setting.experiment_id, emg_electrode_setting.electrode
            )
            electrode_models[
                emg_electrode_setting.electrode.id
            ] = electrode_model_portal
        else:
            electrode_model_portal = electrode_models[
                emg_electrode_setting.electrode.id
            ]

        # electrode setting
        portal_emg_electrode_setting = send_emg_electrode_setting_to_portal(
            portal_emg_setting["id"],
            electrode_model_portal["id"],
            emg_electrode_setting,
        )

        # preamplifier and preamplifier setting
        if hasattr(emg_electrode_setting, "emg_preamplifier_setting"):
            # preamplifier
            portal_preamplifier = send_amplifier_to_portal(
                emg_setting.experiment_id,
                emg_electrode_setting.emg_preamplifier_setting.amplifier,
            )

            # preamplifier setting
            portal_emg_preamplifier_setting = send_emg_preamplifier_setting_to_portal(
                portal_emg_electrode_setting["id"],
                portal_preamplifier["id"],
                emg_electrode_setting.emg_preamplifier_setting,
            )

            # preamplifier filter setting
            if hasattr(
                emg_electrode_setting.emg_preamplifier_setting,
                "emg_preamplifier_filter_setting",
            ):
                # preamplifier filter setting
                emg_preamplifier_filter_setting = send_emg_preamplifier_filter_setting_to_portal(
                    portal_emg_electrode_setting["id"],
                    emg_electrode_setting.emg_preamplifier_setting.emg_preamplifier_filter_setting,
                )

        # amplifier and amplifier setting
        if hasattr(emg_electrode_setting, "emg_amplifier_setting"):
            # amplifier
            portal_amplifier = send_amplifier_to_portal(
                emg_setting.experiment_id,
                emg_electrode_setting.emg_amplifier_setting.amplifier,
            )

            # amplifier setting
            portal_emg_amplifier_setting = send_emg_amplifier_setting_to_portal(
                portal_emg_electrode_setting["id"],
                portal_amplifier["id"],
                emg_electrode_setting.emg_amplifier_setting,
            )

            # analog filter setting
            portal_emg_amplifier_filter_setting = send_emg_analog_filter_setting_to_portal(
                portal_emg_electrode_setting["id"],
                emg_electrode_setting.emg_amplifier_setting.emg_analog_filter_setting,
            )

        # electrode placement setting
        if hasattr(emg_electrode_setting, "emg_electrode_placement_setting"):
            placement_setting = emg_electrode_setting.emg_electrode_placement_setting

            portal_emg_electrode_placement = None

            # surface placement
            if placement_setting.emg_electrode_placement.placement_type == "surface":
                emg_surface_placement = EMGSurfacePlacement.objects.get(
                    pk=placement_setting.emg_electrode_placement.id
                )

                portal_emg_electrode_placement = send_emg_surface_placement_to_portal(
                    emg_setting.experiment_id, emg_surface_placement
                )

            # intramuscular placement
            elif (
                placement_setting.emg_electrode_placement.placement_type
                == "intramuscular"
            ):
                emg_intramuscular_placement = EMGIntramuscularPlacement.objects.get(
                    pk=placement_setting.emg_electrode_placement.id
                )

                portal_emg_electrode_placement = (
                    send_emg_intramuscular_placement_to_portal(
                        emg_setting.experiment_id, emg_intramuscular_placement
                    )
                )

            # needle placement
            else:
                emg_needle_placement = EMGNeedlePlacement.objects.get(
                    pk=placement_setting.emg_electrode_placement.id
                )

                portal_emg_electrode_placement = send_emg_needle_placement_to_portal(
                    emg_setting.experiment_id, emg_needle_placement
                )

            # placement setting
            portal_emg_electrode_placement_setting = (
                send_emg_electrode_placement_setting_to_portal(
                    portal_emg_electrode_setting["id"],
                    portal_emg_electrode_placement["id"],
                    emg_electrode_setting.emg_electrode_placement_setting,
                )
            )

    return portal_emg_setting


def send_tms_device_to_portal(experiment_nes_id, tms_device: TMSDevice):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "manufacturer_name": tms_device.manufacturer.name,
        "equipment_type": tms_device.equipment_type,
        "identification": tms_device.identification,
        "description": tms_device.description,
        "serial_number": tms_device.serial_number,
        "pulse_type": tms_device.pulse_type,
    }

    action_keys = ["experiments", "tms_device", "create"]

    portal_tms_device = rest.client.action(rest.schema, action_keys, params=params)

    return portal_tms_device


def send_coil_model_to_portal(experiment_nes_id, coil_model: CoilModel):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(experiment_nes_id),
        "name": coil_model.name,
        "description": coil_model.description,
        "coil_shape_name": coil_model.coil_shape.name,
        "material_name": coil_model.material.name,
        "material_description": coil_model.material.description,
        "coil_design": coil_model.coil_design,
    }

    action_keys = ["experiments", "coil_model", "create"]

    portal_coil_model = rest.client.action(rest.schema, action_keys, params=params)

    return portal_coil_model


def send_tms_device_setting_to_portal(
    portal_tms_setting_id,
    portal_tms_device_id,
    portal_coil_model_id,
    tms_device_setting: TMSDeviceSetting,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": portal_tms_setting_id,
        "tms_device": portal_tms_device_id,
        "pulse_stimulus_type": tms_device_setting.pulse_stimulus_type,
        "coil_model": portal_coil_model_id,
    }

    action_keys = ["tms_setting", "tms_device_setting", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_tms_setting_to_portal(tms_setting: TMSSetting):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(tms_setting.experiment_id),
        "name": tms_setting.name,
        "description": tms_setting.description,
    }

    action_keys = ["experiments", "tms_setting", "create"]

    portal_tms_setting = rest.client.action(rest.schema, action_keys, params=params)

    # tms device setting
    if hasattr(tms_setting, "tms_device_setting"):
        # tms device
        portal_tms_device = send_tms_device_to_portal(
            tms_setting.experiment_id, tms_setting.tms_device_setting.tms_device
        )

        # coil model
        portal_coil_model = send_coil_model_to_portal(
            tms_setting.experiment_id, tms_setting.tms_device_setting.coil_model
        )

        # tms device setting
        portal_tms_device_setting = send_tms_device_setting_to_portal(
            portal_tms_setting["id"],
            portal_tms_device["id"],
            portal_coil_model["id"],
            tms_setting.tms_device_setting,
        )

    return portal_tms_setting


def send_context_tree_to_portal(context_tree: ContextTree):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(context_tree.experiment_id),
        "name": context_tree.name,
        "description": context_tree.description,
        "setting_text": context_tree.setting_text,
    }

    action_keys = ["experiments", "context_tree", "create"]

    if context_tree.setting_file:
        with open(
            path.join(settings.MEDIA_ROOT, context_tree.setting_file.name), "rb"
        ) as f:
            params["setting_file"] = coreapi.utils.File(
                os.path.basename(context_tree.setting_file.name), f
            )
            portal_group = rest.client.action(
                rest.schema, action_keys, params=params, encoding="multipart/form-data"
            )
    else:
        portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_participant_to_portal(
    schedule_of_sending, portal_group_id, subject: Subject, first_data_collection
):
    rest = RestApiClient()

    if not rest.active:
        return None

    current_language = translation.get_language()
    translation.activate("en")
    gender_name = subject.patient.gender.name.lower()
    translation.activate(current_language)

    date_reference = first_data_collection if first_data_collection else date.today()

    if schedule_of_sending.send_participant_age:
        age = format(
            (date_reference - subject.patient.date_birth) / timedelta(days=365.2425),
            ".4",
        )
    else:
        age = None
    params = {
        "id": portal_group_id,
        "code": subject.patient.code,
        "gender": gender_name,
        "age": age,
    }

    action_keys = ["groups", "participant", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_research_project_to_portal(experiment: Experiment):
    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {
        "experiment_nes_id": str(experiment.id),
        "title": experiment.research_project.title,
        "description": experiment.research_project.description,
        "start_date": experiment.research_project.start_date.strftime("%Y-%m-%d"),
        "keywords": [],
    }

    for keyword in experiment.research_project.keywords.all():
        params["keywords"].append({"name": keyword.name})

    if experiment.research_project.end_date:
        params["end_date"] = experiment.research_project.end_date.strftime("%Y-%m-%d")

    action_keys = ["experiments", "studies", "create"]

    portal_research_project = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_research_project


def send_researcher_to_portal(research_project_id, researcher: User):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "id": research_project_id,
        "first_name": researcher.first_name,
        "last_name": researcher.last_name,
        "email": researcher.email,
        "citation_name": researcher.user_profile.citation_name,
    }

    action_keys = ["studies", "researcher", "create"]

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_experiment_researcher_to_portal(researcher: ExperimentResearcher):
    first_name = ""
    last_name = ""
    citation_name = ""
    citation_order = ""

    if researcher.researcher.first_name:
        first_name = researcher.researcher.first_name

    if researcher.researcher.last_name:
        last_name = researcher.researcher.last_name

    if researcher.researcher.user_profile.citation_name:
        citation_name = researcher.researcher.user_profile.citation_name

    if citation_name == "" and first_name == "" and last_name == "":
        return None

    if researcher.channel_index:
        citation_order = researcher.channel_index

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "experiment_nes_id": str(researcher.experiment.id),
        "first_name": researcher.researcher.first_name,
        "last_name": researcher.researcher.last_name,
        "email": researcher.researcher.email,
        "institution": researcher.researcher.user_profile.institution.name
        if researcher.researcher.user_profile.institution
        else "",
        "citation_name": researcher.researcher.user_profile.citation_name,
        "citation_order": citation_order,
    }

    action_keys = ["experiments", "researchers", "create"]

    return rest.client.action(rest.schema, action_keys, params=params)


def get_experiment_status_portal(experiment_id):
    rest = RestApiClient()

    status = None

    if rest.active:
        try:
            portal_experiment = rest.client.action(
                rest.schema,
                ["experiments", "read"],
                params={"experiment_nes_id": str(experiment_id)},
            )
        except:
            portal_experiment = None

        if portal_experiment and "status" in portal_experiment:
            status = portal_experiment["status"]

    return status


def send_steps_to_portal(
    portal_group_id,
    component_tree,
    list_of_eeg_setting,
    list_of_emg_setting,
    list_of_tms_setting,
    list_of_context_tree,
    language_code,
    component_configuration_id=None,
    parent=None,
):
    component = component_tree["component"]
    component_configuration = None

    if component_configuration_id:
        component_configuration = ComponentConfiguration.objects.get(
            pk=component_configuration_id
        )

    rest = RestApiClient()

    if not rest.active:
        return None

    numeration = (
        component_tree["numeration"] if component_tree["numeration"] != "" else "0"
    )

    survey = None

    # step type
    step_type = component_tree["component_type"]
    if component_tree["component_type"] == "digital_game_phase":
        step_type = "goalkeeper_game"

    params = {
        "id": portal_group_id,
        "identification": component.identification
        + (
            " (" + component_configuration.name + ")"
            if component_configuration and component_configuration.name
            else ""
        ),
        "description": component.description,
        "duration_value": component.duration_value if component.duration_value else 0,
        "duration_unit": component.duration_unit,
        "numeration": numeration,
        "type": step_type,
        "parent": parent,
        "order": component_configuration.order if component_configuration else 0,
        "number_of_repetitions": component_configuration.number_of_repetitions
        if component_configuration
        else None,
        "interval_between_repetitions_value": component_configuration.interval_between_repetitions_value
        if component_configuration
        else None,
        "interval_between_repetitions_unit": component_configuration.interval_between_repetitions_unit
        if component_configuration
        else None,
        "random_position": component_configuration.random_position
        if component_configuration
        else None,
    }

    api_step_method = "step"

    if step_type == "eeg":
        api_step_method = "eeg_step"
        step_specialization = EEG.objects.get(pk=component.id)
        params["eeg_setting"] = list_of_eeg_setting[step_specialization.eeg_setting_id]

    elif step_type == "emg":
        api_step_method = "emg_step"
        step_specialization = EMG.objects.get(pk=component.id)
        params["emg_setting"] = list_of_emg_setting[step_specialization.emg_setting_id]

    elif step_type == "tms":
        api_step_method = "tms_step"
        step_specialization = TMS.objects.get(pk=component.id)
        params["tms_setting"] = list_of_tms_setting[step_specialization.tms_setting_id]

    elif step_type == "instruction":
        api_step_method = "instruction_step"
        step_specialization = Instruction.objects.get(pk=component.id)
        params["text"] = step_specialization.text

    elif step_type == "pause":
        api_step_method = "pause_step"

    elif step_type == "task":
        api_step_method = "task_step"

    elif step_type == "task_experiment":
        api_step_method = "task_for_experimenter_step"

    elif step_type == "generic_data_collection":
        api_step_method = "generic_data_collection_step"
        step_specialization = GenericDataCollection.objects.get(pk=component.id)
        params["information_type_name"] = step_specialization.information_type.name
        params[
            "information_type_description"
        ] = step_specialization.information_type.description

    elif step_type == "stimulus":
        api_step_method = "stimulus_step"
        step_specialization = Stimulus.objects.get(pk=component.id)
        params["stimulus_type_name"] = step_specialization.stimulus_type.name
        if step_specialization.media_file:
            media_file = open(
                path.join(settings.MEDIA_ROOT, step_specialization.media_file.name),
                "rb",
            )
            params["media_file"] = coreapi.utils.File(
                os.path.basename(step_specialization.media_file.name), media_file
            )

    elif step_type == "goalkeeper_game":
        api_step_method = "goalkeeper_game_step"
        step_specialization = DigitalGamePhase.objects.get(pk=component.id)
        params["software_name"] = step_specialization.software_version.software.name
        params[
            "software_description"
        ] = step_specialization.software_version.software.description
        params["software_version"] = step_specialization.software_version.name
        params["context_tree"] = list_of_context_tree[
            step_specialization.context_tree_id
        ]

    elif step_type == "block":
        api_step_method = "set_of_step"
        step_specialization = Block.objects.get(pk=component.id)
        params[
            "number_of_mandatory_steps"
        ] = step_specialization.number_of_mandatory_components
        params["is_sequential"] = (
            True if step_specialization.type == Block.SEQUENCE else False
        )

    elif step_type == "questionnaire":
        api_step_method = "questionnaire_step"
        step_specialization = Questionnaire.objects.get(pk=component.id)
        params["code"] = step_specialization.survey.code
        survey = step_specialization.survey

    action_keys = ["groups", api_step_method, "create"]

    portal_step = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return_dict = {numeration: {"portal_step_id": portal_step["id"]}}

    # Questionnaire step has languages
    if step_type == "questionnaire":
        surveys = Questionnaires()

        # get the main language
        survey_languages = surveys.get_survey_languages(survey.lime_survey_id)

        language = survey_languages["language"]

        survey_metadata, survey_name = get_survey_information(language, survey, surveys)

        params = {
            "id": portal_step["id"],
            "survey_name": survey_name,
            "survey_metadata": survey_metadata,
            "language_code": language,
            "is_default": True,
        }

        action_keys = ["questionnaire_step", "questionnaire_language", "create"]
        rest.client.action(rest.schema, action_keys, params=params)

        if survey_languages["additional_languages"]:
            # additional are not default language
            params["is_default"] = False
            for additional_language in survey_languages["additional_languages"].split(
                " "
            ):
                if additional_language != "":
                    survey_metadata, survey_name = get_survey_information(
                        additional_language, survey, surveys
                    )
                    params["survey_name"] = survey_name
                    params["survey_metadata"] = survey_metadata
                    params["language_code"] = additional_language
                    rest.client.action(rest.schema, action_keys, params=params)

        surveys.release_session_key()

    # Send Step Additional File
    if len(component.component_additional_files.all()) > 0:
        for additional_file in component.component_additional_files.all():
            file = open(path.join(settings.MEDIA_ROOT, additional_file.file.name), "rb")
            params = {
                "id": portal_step["id"],
                "file": coreapi.utils.File(
                    os.path.basename(additional_file.file.name), file
                ),
            }
            action_keys = ["step", "step_additional_file", "create"]
            rest.client.action(
                rest.schema, action_keys, params=params, encoding="multipart/form-data"
            )

    # sending sub-steps
    if component_tree["list_of_component_configuration"]:
        for component_configuration in component_tree[
            "list_of_component_configuration"
        ]:
            sub_step_list = send_steps_to_portal(
                portal_group_id,
                component_configuration["component"],
                list_of_eeg_setting,
                list_of_emg_setting,
                list_of_tms_setting,
                list_of_context_tree,
                language_code,
                component_configuration["id"],
                portal_step["id"],
            )
            return_dict.update(sub_step_list)

    return return_dict


def get_survey_information(language, survey, surveys):
    survey_name = surveys.get_survey_title(survey.lime_survey_id, language)
    questionnaire_utils = QuestionnaireUtils()
    fields = get_questionnaire_fields_for_portal(
        surveys, survey.lime_survey_id, language
    )
    (
        error,
        questionnaire_fields,
    ) = questionnaire_utils.create_questionnaire_explanation_fields(
        survey.lime_survey_id, language, surveys, fields, False
    )
    survey_metadata = ""
    for row in questionnaire_fields:
        first = True
        for column in row:
            survey_metadata += ("," if not first else "") + '"' + str(column) + '"'
            if first:
                first = False

        survey_metadata += "\n"
    return survey_metadata, survey_name


def get_questionnaire_fields_for_portal(
    questionnaire_lime_survey, lime_survey_id, language_code
):
    """
    :param questionnaire_lime_survey: object to get limesurvey info
    :param lime_survey_id: limesurvey id
    :param language_code: the preferred language
    :return: list of fields
    """

    fields = []
    responses_text = questionnaire_lime_survey.get_responses(
        lime_survey_id, language_code
    )
    if responses_text:
        # header
        header_fields = next(reader(StringIO(responses_text), delimiter=","))
        for field in header_fields:
            if field not in questionnaire_evaluation_fields_excluded:
                fields.append(field)

    return fields


def send_file_to_portal(file):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {}

    action_keys = ["files", "create"]

    with open(path.join(settings.MEDIA_ROOT, file), "rb") as f:
        params["file"] = coreapi.utils.File(os.path.basename(file), f)
        portal_file = rest.client.action(
            rest.schema, action_keys, params=params, encoding="multipart/form-data"
        )

    return portal_file


def send_eeg_data_to_portal(
    portal_participant_id,
    portal_step_id,
    portal_file_id_list,
    portal_eeg_setting_id,
    eeg_data: EEGData,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": eeg_data.date.strftime("%Y-%m-%d"),
        "time": eeg_data.time.strftime("%H:%M:%S") if eeg_data.time else None,
        "description": eeg_data.description,
        "file_format": eeg_data.file_format.name,
        "eeg_setting": portal_eeg_setting_id,
        "eeg_cap_size": eeg_data.eeg_cap_size.size if eeg_data.eeg_cap_size else None,
        "eeg_setting_reason_for_change": eeg_data.eeg_setting_reason_for_change,
        "files": [],
    }

    for portal_file_id in portal_file_id_list:
        params["files"].append({"id": portal_file_id})

    action_keys = ["eeg_data", "create"]

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_emg_data_to_portal(
    portal_participant_id,
    portal_step_id,
    portal_file_id_list,
    portal_emg_setting_id,
    emg_data: EMGData,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": emg_data.date.strftime("%Y-%m-%d"),
        "time": emg_data.time.strftime("%H:%M:%S") if emg_data.time else None,
        "description": emg_data.description,
        "file_format": emg_data.file_format.name,
        "emg_setting": portal_emg_setting_id,
        "emg_setting_reason_for_change": emg_data.emg_setting_reason_for_change,
        "files": [],
    }

    for portal_file_id in portal_file_id_list:
        params["files"].append({"id": portal_file_id})

    action_keys = ["emg_data", "create"]

    portal_emg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_emg_data


def send_tms_data_to_portal(
    portal_participant_id, portal_step_id, portal_tms_setting_id, tms_data: TMSData
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": tms_data.date.strftime("%Y-%m-%d"),
        "time": tms_data.time.strftime("%H:%M:%S") if tms_data.time else None,
        "tms_setting": portal_tms_setting_id,
        "resting_motor_threshold": tms_data.resting_motor_threshold,
        "test_pulse_intensity_of_simulation": tms_data.test_pulse_intensity_of_simulation,
        "second_test_pulse_intensity": tms_data.second_test_pulse_intensity,
        "interval_between_pulses": tms_data.interval_between_pulses,
        "interval_between_pulses_unit": tms_data.interval_between_pulses_unit,
        "time_between_mep_trials": tms_data.time_between_mep_trials,
        "time_between_mep_trials_unit": tms_data.time_between_mep_trials_unit,
        "repetitive_pulse_frequency": tms_data.repetitive_pulse_frequency,
        "coil_orientation": tms_data.coil_orientation.name
        if tms_data.coil_orientation
        else None,
        "coil_orientation_angle": tms_data.coil_orientation_angle,
        "direction_of_induced_current": tms_data.direction_of_induced_current.name
        if tms_data.direction_of_induced_current
        else None,
        "description": tms_data.description,
        "hotspot_name": tms_data.hotspot.name,
        "coordinate_x": tms_data.hotspot.coordinate_x,
        "coordinate_y": tms_data.hotspot.coordinate_y,
        "localization_system_name": tms_data.hotspot.tms_localization_system.name,
        "localization_system_description": tms_data.hotspot.tms_localization_system.description,
        "brain_area_name": tms_data.hotspot.tms_localization_system.brain_area.name,
        "brain_area_description": tms_data.hotspot.tms_localization_system.brain_area.description,
        "brain_area_system_name": tms_data.hotspot.tms_localization_system.brain_area.brain_area_system.name,
        "brain_area_system_description": tms_data.hotspot.tms_localization_system.brain_area.brain_area_system.description,
    }

    if tms_data.hotspot and tms_data.hotspot.hot_spot_map:
        hotspot_map = open(
            path.join(settings.MEDIA_ROOT, tms_data.hotspot.hot_spot_map.name), "rb"
        )
        params["hot_spot_map"] = coreapi.utils.File(
            os.path.basename(tms_data.hotspot.hot_spot_map.name), hotspot_map
        )

    if (
        tms_data.hotspot
        and tms_data.hotspot.tms_localization_system.tms_localization_system_image
    ):
        localization_system_image = open(
            path.join(
                settings.MEDIA_ROOT,
                tms_data.hotspot.tms_localization_system.tms_localization_system_image.name,
            ),
            "rb",
        )
        params["localization_system_image"] = coreapi.utils.File(
            os.path.basename(
                tms_data.hotspot.tms_localization_system.tms_localization_system_image.name
            ),
            localization_system_image,
        )

    action_keys = ["tms_data", "create"]

    portal_tms_data = rest.client.action(
        rest.schema, action_keys, params=params, encoding="multipart/form-data"
    )

    return portal_tms_data


def send_digital_game_phase_data_to_portal(
    portal_participant_id,
    portal_step_id,
    portal_file_id_list,
    digital_game_phase_data: DigitalGamePhaseData,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": digital_game_phase_data.date.strftime("%Y-%m-%d"),
        "time": digital_game_phase_data.time.strftime("%H:%M:%S")
        if digital_game_phase_data.time
        else None,
        "description": digital_game_phase_data.description,
        "file_format": digital_game_phase_data.file_format.name,
        "sequence_used_in_context_tree": digital_game_phase_data.sequence_used_in_context_tree,
        "files": [],
    }

    for portal_file_id in portal_file_id_list:
        params["files"].append({"id": portal_file_id})

    action_keys = ["goalkeeper_game_data", "create"]

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_questionnaire_response_to_portal(
    portal_participant_id,
    portal_step_id,
    limesurvey_response,
    questionnaire_response: QuestionnaireResponse,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": questionnaire_response.date.strftime("%Y-%m-%d"),
        "time": questionnaire_response.time.strftime("%H:%M:%S")
        if questionnaire_response.time
        else None,
        "limesurvey_response": limesurvey_response,
    }

    action_keys = ["questionnaire_response", "create"]

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_additional_data_to_portal(
    portal_participant_id,
    portal_step_id,
    portal_file_id_list,
    additional_data: AdditionalData,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": additional_data.date.strftime("%Y-%m-%d"),
        "time": additional_data.time.strftime("%H:%M:%S")
        if additional_data.time
        else None,
        "description": additional_data.description,
        "file_format": additional_data.file_format.name,
        "files": [],
    }

    for portal_file_id in portal_file_id_list:
        params["files"].append({"id": portal_file_id})

    action_keys = ["additional_data", "create"]

    portal_additional_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_additional_data


def send_generic_data_collection_data_to_portal(
    portal_participant_id,
    portal_step_id,
    portal_file_id_list,
    generic_data_collection_data: GenericDataCollectionData,
):
    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": generic_data_collection_data.date.strftime("%Y-%m-%d"),
        "time": generic_data_collection_data.time.strftime("%H:%M:%S")
        if generic_data_collection_data.time
        else None,
        "description": generic_data_collection_data.description,
        "file_format": generic_data_collection_data.file_format.name,
        "files": [],
    }

    for portal_file_id in portal_file_id_list:
        params["files"].append({"id": portal_file_id})

    action_keys = ["generic_data_collection_data", "create"]

    portal_generic_data_collection_data = rest.client.action(
        rest.schema, action_keys, params=params
    )

    return portal_generic_data_collection_data
