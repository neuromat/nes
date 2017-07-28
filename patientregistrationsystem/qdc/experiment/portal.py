import coreapi
import os

from datetime import date, timedelta

from os import path

from django.conf import settings
from django.utils import translation

from .models import Experiment, Group, Subject, TeamPerson, User, EEGSetting, EMGSetting, TMSSetting, ContextTree, \
    ComponentConfiguration, EEGData, EMGData, TMSData, DigitalGamePhaseData, QuestionnaireResponse, \
    GenericDataCollectionData, AdditionalData, EEG, EMG, TMS, Instruction, GenericDataCollection, Stimulus, \
    DigitalGamePhase, Block, Questionnaire

# from export.export import ExportExecution

from survey.abc_search_engine import Questionnaires
from survey.views import get_questionnaire_language


class RestApiClient(object):
    client = None
    schema = None
    active = False

    def __init__(self):
        auth = coreapi.auth.BasicAuthentication(username=settings.PORTAL_API['USER'],
                                                password=settings.PORTAL_API['PASSWORD'])
        self.client = coreapi.Client(auth=auth)

        try:
            url = settings.PORTAL_API['URL'] + \
                  (':' + settings.PORTAL_API['PORT'] if settings.PORTAL_API['PORT'] else '') + \
                  '/api/schema/'

            self.schema = self.client.get(url)
            self.active = True
        except:
            self.active = False


def get_portal_status():
    return RestApiClient().active


# def send_user_to_portal(user):
#
#     rest = RestApiClient()
#
#     if not rest.active:
#         return None
#
#     try:
#         portal_user = rest.client.action(
#             rest.schema, ['researchers', 'read'], params={"nes_id": str(user.id)})
#
#     except:
#         portal_user = None
#
#     # general params
#     params = {"nes_id": str(user.id),
#               "first_name": user.first_name,
#               "surname": user.last_name,
#               "email": user.email}
#
#     # create or update
#     if portal_user:
#         # params["id"] = portal_user['id']
#
#         portal_user = rest.client.action(
#             rest.schema, ['researchers', 'update'], params=params)
#     else:
#         portal_user = rest.client.action(
#             rest.schema, ['researchers', 'create'], params=params)
#
#     return portal_user


def send_experiment_to_portal(experiment: Experiment):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"nes_id": str(experiment.id),
              "title": experiment.title,
              "description": experiment.description,
              "data_acquisition_done": str(experiment.data_acquisition_is_concluded),
              "project_url": experiment.source_code_url,
              "ethics_committee_url": experiment.ethics_committee_project_url
              }

    action_keys = ['experiments', 'create']

    if experiment.ethics_committee_project_file:
        with open(path.join(settings.MEDIA_ROOT, experiment.ethics_committee_project_file.name), 'rb') as f:
            params["ethics_committee_file"] = \
                coreapi.utils.File(os.path.basename(experiment.ethics_committee_project_file.name), f)

            portal_experiment = rest.client.action(rest.schema, action_keys,
                                                   params=params, encoding="multipart/form-data")
    else:
        portal_experiment = rest.client.action(rest.schema, action_keys,
                                               params=params, encoding="multipart/form-data")

    return portal_experiment


def send_experiment_end_message_to_portal(experiment: Experiment):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(experiment.id),
              "nes_id": str(experiment.id),
              "status": "to_be_analysed",
              "title": experiment.title,
              "description": experiment.description
              }

    action_keys = ['experiments', 'update']

    portal_experiment = rest.client.action(rest.schema, action_keys, params=params)

    return portal_experiment


def send_group_to_portal(group: Group):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(group.experiment.id),
              "title": group.title,
              "description": group.description,
              "inclusion_criteria": []
              }

    for criteria in group.classification_of_diseases.all():
        params['inclusion_criteria'].append({'code': criteria.code})

    action_keys = ['experiments', 'groups', 'create']

    portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_experimental_protocol_to_portal(portal_group_id, textual_description, image, root_step_id):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {"id": portal_group_id}

    if textual_description:
        params["textual_description"] = textual_description

    if root_step_id:
        params["root_step"] = root_step_id

    action_keys = ['groups', 'experimental_protocol', 'create']

    if image:
        with open(settings.BASE_DIR + image, 'rb') as f:
            params["image"] = coreapi.utils.File(os.path.basename(image), f)
            portal_experimental_protocol = rest.client.action(rest.schema, action_keys,
                                                              params=params, encoding="multipart/form-data")
    else:
        portal_experimental_protocol = rest.client.action(rest.schema, action_keys, params=params)

    return portal_experimental_protocol


def send_eeg_setting_to_portal(eeg_setting: EEGSetting):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(eeg_setting.experiment_id),
              "name": eeg_setting.name,
              "description": eeg_setting.description,
              }

    action_keys = ['experiments', 'eeg_setting', 'create']

    portal_eeg_setting = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_setting


def send_emg_setting_to_portal(emg_setting: EMGSetting):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(emg_setting.experiment_id),
              "name": emg_setting.name,
              "description": emg_setting.description,
              'acquisition_software_version':
                  emg_setting.acquisition_software_version.software.name + " " +
                  emg_setting.acquisition_software_version.name
              }

    action_keys = ['experiments', 'emg_setting', 'create']

    portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_tms_setting_to_portal(tms_setting: TMSSetting):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(tms_setting.experiment_id),
              "name": tms_setting.name,
              "description": tms_setting.description,
              }

    action_keys = ['experiments', 'tms_setting', 'create']

    portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_context_tree_to_portal(context_tree: ContextTree):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(context_tree.experiment_id),
              "name": context_tree.name,
              "description": context_tree.description,
              'setting_text': context_tree.setting_text
              }

    action_keys = ['experiments', 'context_tree', 'create']

    if context_tree.setting_file:
        with open(path.join(settings.MEDIA_ROOT, context_tree.setting_file.name), 'rb') as f:
            params["setting_file"] = coreapi.utils.File(os.path.basename(context_tree.setting_file.name), f)
            portal_group = rest.client.action(rest.schema, action_keys, params=params, encoding="multipart/form-data")
    else:
        portal_group = rest.client.action(rest.schema, action_keys, params=params)

    return portal_group


def send_participant_to_portal(portal_group_id, subject: Subject):

    rest = RestApiClient()

    if not rest.active:
        return None

    current_language = translation.get_language()
    translation.activate('en')
    gender_name = subject.patient.gender.name.lower()
    translation.activate(current_language)

    params = {"id": portal_group_id,
              "code": subject.patient.code,
              "gender": gender_name,
              "age": format((date.today() - subject.patient.date_birth) / timedelta(days=365.2425), '.4')}

    action_keys = ['groups', 'participant', 'create']

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_research_project_to_portal(experiment: Experiment):

    rest = RestApiClient()

    if not rest.active:
        return None

    # general params
    params = {"experiment_nes_id": str(experiment.id),
              "title": experiment.research_project.title,
              "description": experiment.research_project.description,
              "start_date": experiment.research_project.start_date.strftime("%Y-%m-%d"),
              "keywords": []
              }

    for keyword in experiment.research_project.keywords.all():
        params['keywords'].append({'name': keyword.name})

    if experiment.research_project.end_date:
        params["end_date"] = experiment.research_project.end_date.strftime("%Y-%m-%d")

    action_keys = ['experiments', 'studies', 'create']

    portal_research_project = rest.client.action(rest.schema, action_keys , params=params)

    return portal_research_project


def send_collaborator_to_portal(research_project_id, team_person: TeamPerson):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {"id": research_project_id,
              "name": team_person.person.first_name + ' ' + team_person.person.last_name,
              "team": team_person.team.name,
              "coordinator": team_person.is_coordinator}

    action_keys = ['studies', 'collaborators', 'create']

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def send_researcher_to_portal(research_project_id, researcher: User):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {"id": research_project_id,
              "name": researcher.first_name + ' ' + researcher.last_name,
              "email": researcher.email}

    action_keys = ['studies', 'researcher', 'create']

    portal_participant = rest.client.action(rest.schema, action_keys, params=params)

    return portal_participant


def get_experiment_status_portal(experiment_id):

    rest = RestApiClient()

    status = None

    if rest.active:

        try:
            portal_experiment = rest.client.action(
                rest.schema, ['experiments', 'read'], params={"experiment_nes_id": str(experiment_id)})
        except:
            portal_experiment = None

        if portal_experiment and 'status' in portal_experiment:
            status = portal_experiment['status']

    return status


def send_steps_to_portal(portal_group_id, component_tree,
                         list_of_eeg_setting, list_of_emg_setting, list_of_tms_setting, list_of_context_tree,
                         language_code,
                         component_configuration_id=None, parent=None,):

    component = component_tree['component']
    component_configuration = None

    if component_configuration_id:
        component_configuration = ComponentConfiguration.objects.get(pk=component_configuration_id)

    rest = RestApiClient()

    if not rest.active:
        return None

    numeration = component_tree['numeration'] if component_tree['numeration'] != '' else '0'

    # step type
    step_type = component_tree['component_type']
    if component_tree['component_type'] == "digital_game_phase":
        step_type = "goalkeeper_game"

    params = {"id": portal_group_id,
              'identification':
                  component.identification + (' (' + component_configuration.name + ')'
                                              if component_configuration and component_configuration.name else ''),
              'description': component.description,
              'duration_value': component.duration_value if component.duration_value else 0,
              'duration_unit': component.duration_unit,
              'numeration': numeration,
              'type': step_type,
              'parent': parent,
              'order': component_configuration.order if component_configuration else 0,
              'number_of_repetitions':
                  component_configuration.number_of_repetitions if component_configuration else None,
              'interval_between_repetitions_value':
                  component_configuration.interval_between_repetitions_value if component_configuration else None,
              'interval_between_repetitions_unit':
                  component_configuration.interval_between_repetitions_unit if component_configuration else None,
              'random_position':
                  component_configuration.random_position if component_configuration else None}

    api_step_method = 'step'

    if step_type == "eeg":
        api_step_method = 'eeg_step'
        step_specialization = EEG.objects.get(pk=component.id)
        params['eeg_setting'] = list_of_eeg_setting[step_specialization.eeg_setting_id]

    elif step_type == "emg":
        api_step_method = 'emg_step'
        step_specialization = EMG.objects.get(pk=component.id)
        params['emg_setting'] = list_of_emg_setting[step_specialization.emg_setting_id]

    elif step_type == "tms":
        api_step_method = 'tms_step'
        step_specialization = TMS.objects.get(pk=component.id)
        params['tms_setting'] = list_of_tms_setting[step_specialization.tms_setting_id]

    elif step_type == "instruction":
        api_step_method = 'instruction_step'
        step_specialization = Instruction.objects.get(pk=component.id)
        params['text'] = step_specialization.text

    elif step_type == "pause":
        api_step_method = 'pause_step'

    elif step_type == "task":
        api_step_method = 'task_step'

    elif step_type == "task_experiment":
        api_step_method = 'task_for_experimenter_step'

    elif step_type == "generic_data_collection":
        api_step_method = 'generic_data_collection_step'
        step_specialization = GenericDataCollection.objects.get(pk=component.id)
        params['information_type_name'] = step_specialization.information_type.name
        params['information_type_description'] = step_specialization.information_type.description

    elif step_type == "stimulus":
        api_step_method = 'stimulus_step'
        step_specialization = Stimulus.objects.get(pk=component.id)
        params['stimulus_type_name'] = step_specialization.stimulus_type.name
        if step_specialization.media_file:
            media_file = open(path.join(settings.MEDIA_ROOT, step_specialization.media_file.name), 'rb')
            params["media_file"] = \
                coreapi.utils.File(
                    os.path.basename(step_specialization.media_file.name),
                    media_file)

    elif step_type == "goalkeeper_game":
        api_step_method = 'goalkeeper_game_step'
        step_specialization = DigitalGamePhase.objects.get(pk=component.id)
        params['software_name'] = step_specialization.software_version.software.name
        params['software_description'] = step_specialization.software_version.software.description
        params['software_version'] = step_specialization.software_version.name
        params['context_tree'] = list_of_context_tree[step_specialization.context_tree_id]

    elif step_type == "block":
        api_step_method = 'set_of_step'
        step_specialization = Block.objects.get(pk=component.id)
        params['number_of_mandatory_steps'] = step_specialization.number_of_mandatory_components
        params['is_sequential'] = True if step_specialization.type == Block.SEQUENCE else False

    elif step_type == "questionnaire":
        api_step_method = 'questionnaire_step'

        surveys = Questionnaires()
        step_specialization = Questionnaire.objects.get(pk=component.id)
        language = get_questionnaire_language(surveys, step_specialization.survey.lime_survey_id, language_code)
        params['survey_name'] = surveys.get_survey_title(step_specialization.survey.lime_survey_id, language)
        params['survey_metadata'] = "teste"

        # export = ExportExecution(0, 0)

        # fields = export.get_questionnaire_experiment_fields(step_specialization.survey.id)
        # questionnaire_fields = export.create_questionnaire_explanation_fields_file(
        #     str(step_specialization.survey.id), language, surveys, fields, False)

        surveys.release_session_key()

    action_keys = ['groups', api_step_method, 'create']

    portal_step = rest.client.action(rest.schema, action_keys, params=params, encoding="multipart/form-data")

    return_dict = {numeration: {'portal_step_id': portal_step['id']}}

    if component_tree['list_of_component_configuration']:
        for component_configuration in component_tree['list_of_component_configuration']:
            sub_step_list = send_steps_to_portal(portal_group_id,
                                                 component_configuration['component'],
                                                 list_of_eeg_setting,
                                                 list_of_emg_setting,
                                                 list_of_tms_setting,
                                                 list_of_context_tree,
                                                 language_code,
                                                 component_configuration['id'],
                                                 portal_step['id'])
            return_dict.update(sub_step_list)

    return return_dict


def send_file_to_portal(file):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {}

    action_keys = ['files', 'create']

    with open(path.join(settings.MEDIA_ROOT, file), 'rb') as f:
        params["file"] = coreapi.utils.File(os.path.basename(file), f)
        portal_file = rest.client.action(rest.schema, action_keys, params=params, encoding="multipart/form-data")

    return portal_file


def send_eeg_data_to_portal(portal_participant_id, portal_step_id, portal_file_id, portal_eeg_setting_id,
                            eeg_data: EEGData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "file": portal_file_id,
        "date": eeg_data.date.strftime("%Y-%m-%d"),
        "time": eeg_data.time.strftime('%H:%M:%S') if eeg_data.time else None,
        "description": eeg_data.description,
        "file_format": eeg_data.file_format.name,
        "eeg_setting": portal_eeg_setting_id,
        "eeg_cap_size": eeg_data.eeg_cap_size.size if eeg_data.eeg_cap_size else None,
        "eeg_setting_reason_for_change": eeg_data.eeg_setting_reason_for_change
    }

    action_keys = ['eeg_data', 'create']

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_emg_data_to_portal(portal_participant_id, portal_step_id, portal_file_id, portal_emg_setting_id,
                            emg_data: EMGData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "file": portal_file_id,
        "date": emg_data.date.strftime("%Y-%m-%d"),
        "time": emg_data.time.strftime('%H:%M:%S') if emg_data.time else None,
        "description": emg_data.description,
        "file_format": emg_data.file_format.name,
        "emg_setting": portal_emg_setting_id,
        "emg_setting_reason_for_change": emg_data.emg_setting_reason_for_change
    }

    action_keys = ['emg_data', 'create']

    portal_emg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_emg_data


def send_tms_data_to_portal(portal_participant_id, portal_step_id, portal_tms_setting_id,
                            tms_data: TMSData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": tms_data.date.strftime("%Y-%m-%d"),
        "time": tms_data.time.strftime('%H:%M:%S') if tms_data.time else None,
        "tms_setting": portal_tms_setting_id,
        "resting_motor_threshold": tms_data.resting_motor_threshold,
        "test_pulse_intensity_of_simulation": tms_data.test_pulse_intensity_of_simulation,
        "second_test_pulse_intensity": tms_data.second_test_pulse_intensity,
        "interval_between_pulses": tms_data.interval_between_pulses,
        "interval_between_pulses_unit": tms_data.interval_between_pulses_unit,
        "time_between_mep_trials": tms_data.time_between_mep_trials,
        "time_between_mep_trials_unit": tms_data.time_between_mep_trials_unit,
        "repetitive_pulse_frequency": tms_data.repetitive_pulse_frequency,
        "coil_orientation": tms_data.coil_orientation.name if tms_data.coil_orientation else None,
        "coil_orientation_angle": tms_data.coil_orientation_angle,
        "direction_of_induced_current":
            tms_data.direction_of_induced_current.name if tms_data.direction_of_induced_current else None,
        "description": tms_data.description,
        "hotspot_name": tms_data.hotspot.name,
        "coordinate_x": tms_data.hotspot.coordinate_x,
        "coordinate_y": tms_data.hotspot.coordinate_y,
        "localization_system_name": tms_data.hotspot.tms_localization_system.name,
        "localization_system_description": tms_data.hotspot.tms_localization_system.description,
        "brain_area_name": tms_data.hotspot.tms_localization_system.brain_area.name,
        "brain_area_description": tms_data.hotspot.tms_localization_system.brain_area.description,
        "brain_area_system_name": tms_data.hotspot.tms_localization_system.brain_area.brain_area_system.name,
        "brain_area_system_description":
            tms_data.hotspot.tms_localization_system.brain_area.brain_area_system.description
    }

    if tms_data.hotspot and tms_data.hotspot.hot_spot_map:
        hotspot_map = open(path.join(settings.MEDIA_ROOT, tms_data.hotspot.hot_spot_map.name), 'rb')
        params["hot_spot_map"] =\
            coreapi.utils.File(
                os.path.basename(tms_data.hotspot.hot_spot_map.name),
                hotspot_map)

    if tms_data.hotspot and tms_data.hotspot.tms_localization_system.tms_localization_system_image:
        localization_system_image = \
            open(path.join(settings.MEDIA_ROOT,
                           tms_data.hotspot.tms_localization_system.tms_localization_system_image.name), 'rb')
        params["localization_system_image"] = \
            coreapi.utils.File(
                os.path.basename(tms_data.hotspot.tms_localization_system.tms_localization_system_image.name),
                localization_system_image)

    action_keys = ['tms_data', 'create']

    portal_tms_data = rest.client.action(rest.schema, action_keys, params=params, encoding="multipart/form-data")

    return portal_tms_data


def send_digital_game_phase_data_to_portal(portal_participant_id, portal_step_id, portal_file_id,
                                           digital_game_phase_data: DigitalGamePhaseData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "file": portal_file_id,
        "date": digital_game_phase_data.date.strftime("%Y-%m-%d"),
        "time": digital_game_phase_data.time.strftime('%H:%M:%S') if digital_game_phase_data.time else None,
        "description": digital_game_phase_data.description,
        "file_format": digital_game_phase_data.file_format.name,
        "sequence_used_in_context_tree": digital_game_phase_data.sequence_used_in_context_tree
    }

    action_keys = ['goalkeeper_game_data', 'create']

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_questionnaire_response_to_portal(portal_participant_id, portal_step_id, limesurvey_response,
                                          questionnaire_response: QuestionnaireResponse):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "date": questionnaire_response.date.strftime("%Y-%m-%d"),
        "time": questionnaire_response.time.strftime('%H:%M:%S') if questionnaire_response.time else None,
        "limesurvey_response": limesurvey_response
    }

    action_keys = ['questionnaire_response', 'create']

    portal_eeg_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_eeg_data


def send_additional_data_to_portal(portal_participant_id, portal_step_id, portal_file_id,
                                   additional_data: AdditionalData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "file": portal_file_id,
        "date": additional_data.date.strftime("%Y-%m-%d"),
        "time": additional_data.time.strftime('%H:%M:%S') if additional_data.time else None,
        "description": additional_data.description,
        "file_format": additional_data.file_format.name,
    }

    action_keys = ['additional_data', 'create']

    portal_additional_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_additional_data


def send_generic_data_collection_data_to_portal(portal_participant_id, portal_step_id, portal_file_id,
                                                generic_data_collection_data: GenericDataCollectionData):

    rest = RestApiClient()

    if not rest.active:
        return None

    params = {
        "participant": portal_participant_id,
        "step": portal_step_id,
        "file": portal_file_id,
        "date": generic_data_collection_data.date.strftime("%Y-%m-%d"),
        "time": generic_data_collection_data.time.strftime('%H:%M:%S') if generic_data_collection_data.time else None,
        "description": generic_data_collection_data.description,
        "file_format": generic_data_collection_data.file_format.name,
    }

    action_keys = ['generic_data_collection_data', 'create']

    portal_generic_data_collection_data = rest.client.action(rest.schema, action_keys, params=params)

    return portal_generic_data_collection_data
