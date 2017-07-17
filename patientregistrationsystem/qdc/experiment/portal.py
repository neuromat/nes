import coreapi
import os

from datetime import date, timedelta

from os import path

from django.conf import settings
from django.utils import translation

from .models import Experiment, Group, Subject, TeamPerson, User, EEGSetting, EMGSetting, TMSSetting, ContextTree, \
    ComponentConfiguration, EEGData, EMGData, DigitalGamePhaseData, QuestionnaireResponse


class RestApiClient(object):
    client = None
    schema = None
    active = False

    def __init__(self):
        auth = coreapi.auth.BasicAuthentication(username=settings.PORTAL_API['USER'],
                                                password=settings.PORTAL_API['PASSWORD'])
        self.client = coreapi.Client(auth=auth)

        try:
            self.schema = self.client.get(settings.PORTAL_API['URL'] + ':' +
                                          settings.PORTAL_API['PORT'] + '/api/schema/')
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
              "status": "to_be_analysed"
              }

    action_keys = ['experiments', 'partial_update']

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


def send_steps_to_portal(portal_group_id, component_tree, component_configuration_id=None, parent=None):

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

    action_keys = ['groups', 'step', 'create']

    portal_step = rest.client.action(rest.schema, action_keys, params=params)

    return_dict = {numeration: {'portal_step_id': portal_step['id']}}

    if component_tree['list_of_component_configuration']:
        for component_configuration in component_tree['list_of_component_configuration']:
            sub_step_list = send_steps_to_portal(portal_group_id,
                                                 component_configuration['component'],
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
