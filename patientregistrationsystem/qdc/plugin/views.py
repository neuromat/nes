import os
from operator import itemgetter
from os import path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from export.input_export import build_complete_export_structure
from export.models import Export
from export.views import patient_fields, get_questionnaire_fields, export_create
from patient.models import QuestionnaireResponse
from plugin.models import RandomForests
from survey.models import Survey


def participants_dict(survey):
    """
    Function to check who answered a questionnaire
    :param survey: Which questionnaire will be checked
    :return: Participants that answered the survey
    """
    participants = {}

    for response in QuestionnaireResponse.objects.filter(survey=survey).filter(patient__removed=False):
        participants[response.patient.id] = {
            'patient_id': response.patient.id,
            'patient_name': response.patient.name if response.patient.name else response.patient.code,
        }

    return participants


def update_patient_attributes(participants):
    """add item to 'patient_selected POST list to suit to export method
    :param participants: list - participants
    :return: list - updated participants
    """
    participant_attributes = participants
    participants = [['code', 'participant_code']]  # First entry is that (see export)
    for participant in participant_attributes:
        participants.append(participant.split('*'))

    return participants


def build_questionnaires_list(language_code):
    """Build questionnaires list that will be used in export method to build
    export structure
    :param language_code: str - questionnaire language code
    :return: list - questionnaires
    """
    random_forests = get_object_or_404(RandomForests)
    surveys = [
        random_forests.admission_assessment.lime_survey_id, random_forests.surgical_evaluation.lime_survey_id
    ]
    questionnaires = get_questionnaire_fields(surveys, language_code)
    # Transform questionnaires (to get the format of build_complete_export_structure
    # questionnaires list argument)
    for i, questionnaire in enumerate(questionnaires):
        questionnaire['index'] = str(i)
    questionnaires = [
        [
            dict0['index'], dict0['sid'], dict0['title'],
            [
                (dict1['header'], dict1['field']) for index1, dict1 in enumerate(dict0['output_list'])
            ]
        ]
        for index, dict0 in enumerate(questionnaires)
    ]

    return questionnaires


def build_zip_file(request, participants, questionnaires):
    """Define components to use as the component list argument of
    build_complete_export_structure export method
    :param request:
    :param participants:
    :param questionnaires:
    :return:
    """
    components = {
        'per_additional_data': False, 'per_eeg_nwb_data': False, 'per_eeg_raw_data': False,
        'per_emg_data': False, 'per_generic_data': False, 'per_goalkeeper_game_data': False,
        'per_stimulus_data': False, 'per_tms_data': False
    }
    export = Export.objects.create(user=request.user)
    export_dir = path.join(settings.MEDIA_ROOT, 'export', str(request.user.id), str(export.id))
    os.makedirs(export_dir)
    input_filename = path.join(export_dir, 'json_export.json')
    build_complete_export_structure(
        True, True, False, participants, [], questionnaires, [], ['short'], 'code',
        input_filename, components, request.LANGUAGE_CODE, 'csv')
    zip_file = export_create(request, export.id, input_filename)

    return zip_file


@login_required
def send_to_plugin(request, template_name="plugin/send_to_plugin.html"):
    if request.method == 'POST':
        participants = update_patient_attributes(request.POST.getlist('patient_selected'))
        questionnaires = build_questionnaires_list(request.LANGUAGE_CODE)
        zip_file = build_zip_file(request, participants, questionnaires)
        if zip_file:
            messages.success(request, _('Data from questionnaires was sent to Forest Plugin'))
            with open(zip_file, 'rb') as file:
                response = HttpResponse(file, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="export.zip"'
                response['Content-Lenght'] = path.getsize(zip_file)
                return response
        else:
            messages.error(request, _('Could not open zip file to send to Forest Plugin'))

    try:
        random_forests = RandomForests.objects.get()
    except RandomForests.DoesNotExist:
        random_forests = None

    admission_participants = {}
    surgical_participants = {}

    # Patients that answered the admission assessment questionnaire
    if random_forests and random_forests.admission_assessment:
        admission = Survey.objects.get(pk=random_forests.admission_assessment.pk)
        admission_participants = participants_dict(admission)

    # Patients that answered the surgical evaluation questionnaire
    if random_forests and random_forests.surgical_evaluation:
        surgical = Survey.objects.get(pk=random_forests.surgical_evaluation.pk)
        surgical_participants = participants_dict(surgical)

    # The intersection of admission assessment and surgical evaluation questionnaires
    intersection_dict = {}
    for i in admission_participants:
        if i in surgical_participants and admission_participants[i] == surgical_participants[i]:
            intersection_dict[i] = admission_participants[i]

    # Transform the intersection dictionary into a list, so that we can sort it by patient name
    participants = []

    for key, dictionary in list(intersection_dict.items()):
        dictionary['patient_id'] = key
        participants.append(dictionary)

    participants = sorted(participants, key=itemgetter('patient_name'))

    context = {
        'participants': participants,
        'patient_fields': patient_fields
    }

    return render(request, template_name, context)
