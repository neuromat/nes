from operator import itemgetter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from export.views import patient_fields
from plugin.models import RandomForests
from survey.models import Survey
from patient.models import QuestionnaireResponse


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
            'patient_name': response.patient.name,
        }

    return participants


@login_required
def send_to_plugin(request, template_name="plugin/send_to_plugin.html"):
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

    # Transform the intersection dictionary into a list, so that we can sort it by patient name.
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
