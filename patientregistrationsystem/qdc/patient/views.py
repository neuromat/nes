# coding=utf-8
import datetime
import re

from functools import partial
from operator import itemgetter

from django.contrib import messages
from django.contrib.auth import PermissionDenied
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.cache import cache

from experiment.models import Subject, SubjectOfGroup, \
    QuestionnaireResponse as ExperimentQuestionnaireResponse, Questionnaire

from patient.forms import QuestionnaireResponseForm
from patient.forms import PatientForm, TelephoneForm, \
    SocialDemographicDataForm, SocialHistoryDataForm, ComplementaryExamForm,\
    ExamFileForm
from patient.models import Patient, Telephone, SocialDemographicData,\
    SocialHistoryData, MedicalRecordData, ClassificationOfDiseases, Diagnosis,\
    ExamFile, ComplementaryExam, QuestionnaireResponse

from survey.abc_search_engine import Questionnaires
from survey.models import Survey
from survey.survey_utils import find_questionnaire_name
from survey.views import get_questionnaire_responses, check_limesurvey_access, \
    get_questionnaire_language, csv_to_list

# pylint: disable=E1101
# pylint: disable=E1103

permission_required = partial(permission_required, raise_exception=True)


@login_required
@permission_required('patient.view_patient')
def patient_view(request, patient_id):
    current_tab = get_current_tab(request)
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == "POST":
        redirect_url = reverse("search_patient")

        if 'action' in request.POST:
            if request.POST['action'] == "remove":
                patient.removed = True
                patient.save()
            elif request.POST['action'] == "show_previous":
                redirect_url = reverse("patient_view", args=(patient_id,))
                return HttpResponseRedirect(
                    redirect_url + "?currentTab=" + str(int(current_tab) - 1))
            elif request.POST['action'] == "show_next":
                redirect_url = reverse("patient_view", args=(patient_id,))
                return HttpResponseRedirect(
                    redirect_url + "?currentTab=" + str(int(current_tab) + 1))
            else:
                redirect_url = reverse("patient_edit", args=(patient_id,))
                return HttpResponseRedirect(
                    redirect_url + "?currentTab=" + current_tab)

        return HttpResponseRedirect(redirect_url)

    if patient and not patient.removed:
        context = {
            'editing': False,
            'currentTab': current_tab,
            'patient_id': patient_id}

        if current_tab == '0':
            return patient_view_personal_data(request, patient, context)
        elif current_tab == '1':
            return patient_view_social_demographic_data(
                request, patient, context)
        elif current_tab == '2':
            return patient_view_social_history(request, patient, context)
        elif current_tab == '3':
            return patient_view_medical_record(request, patient, context)
        else:  # current_tab == '4':
            if request.user.has_perm('survey.view_survey'):
                return patient_view_questionnaires(
                    request, patient, context, False)
            else:
                raise PermissionDenied


@login_required
@permission_required('patient.add_patient')
def patient_create(request, template_name="patient/register_personal_data.html"):
    patient_form = PatientForm(request.POST or None)
    telephone_inlineformset = inlineformset_factory(
        Patient, Telephone, form=TelephoneForm)

    if request.method == 'POST':
        patient_form.city = request.POST['city'] \
            if 'city' in request.POST \
            else ''
        telephone_formset = telephone_inlineformset(
            request.POST, request.FILES)

        if patient_form.is_valid() and telephone_formset.is_valid():
            new_patient = patient_form.save(commit=False)

            # Remove leading and trailing white spaces to avoid problems with
            # homonym search.
            if new_patient.name:
                new_patient.name = new_patient.name.strip()

            if not new_patient.cpf:
                new_patient.cpf = None

            new_patient.changed_by = request.user
            new_patient.save()
            new_phone_list = telephone_formset.save(commit=False)

            for phone in new_phone_list:
                phone.changed_by = request.user
                phone.patient = new_patient
                phone.save()

            messages.success(request, _('Personal data successfully written.'))
            return finish_handling_post(request, new_patient.id, 0)

        else:
            if request.POST['cpf']:
                patient_found = Patient.objects.filter(cpf=request.POST['cpf'])

                if patient_found:
                    if patient_found[0].removed:
                        patient_form.errors['cpf'][0] = _("Participant with this CPF has already removed.")
                    else:
                        patient_form.errors['cpf'][0] = _("There is already registered participant with this CPF.")

    else:
        telephone_formset = telephone_inlineformset()

    context = {
        'patient_form': patient_form,
        'telephone_formset': telephone_formset,
        'editing': True,
        'inserting': True,
        'currentTab': '0'
    }

    return render(request, template_name, context)


@login_required
@permission_required('patient.change_patient')
def patient_update(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if patient and not patient.removed:
        current_tab = get_current_tab(request)

        context = {
            'editing': True,
            'currentTab': current_tab,
            'patient_id': patient_id}

        if current_tab == '0':
            return patient_update_personal_data(request, patient, context)
        elif current_tab == '1':
            return patient_update_social_demographic_data(
                request, patient, context)
        elif current_tab == '2':
            return patient_update_social_history(request, patient, context)
        elif current_tab == '3':
            return patient_update_medical_record(request, patient, context)
        else:  # current_tab == '4'
            if request.user.has_perm('survey.view_survey'):
                return patient_view_questionnaires(
                    request, patient, context, True)
            else:
                raise PermissionDenied


def get_current_tab(request):
    current_tab = '0'

    if request.method == "POST":
        if 'currentTab' in request.POST:
            current_tab = request.POST['currentTab']
    else:
        if 'currentTab' in request.GET:
            current_tab = request.GET['currentTab']

    return current_tab


def patient_update_personal_data(request, patient, context):
    patient_form = PatientForm(request.POST or None, instance=patient)

    telephone_inlineformset = inlineformset_factory(Patient, Telephone, form=TelephoneForm)

    if not patient.name:
        patient_form.fields['anonymous'].widget.attrs['checked'] = True

    if request.method == "POST":
        patient_form_is_valid = patient_form.is_valid()

        telephone_formset = telephone_inlineformset(request.POST, request.FILES, instance=patient)
        telephone_formset_is_valid = telephone_formset.is_valid()

        if patient_form_is_valid and telephone_formset_is_valid:
            patient_form_has_changed = patient_form.has_changed()
            telephone_formset_has_changed = telephone_formset.has_changed()

            if patient_form_has_changed:
                new_patient = patient_form.save(commit=False)

                if not new_patient.cpf:
                    new_patient.cpf = None

                new_patient.changed_by = request.user
                new_patient.save()

            if telephone_formset_has_changed:
                new_phone_list = telephone_formset.save(commit=False)

                for phone in new_phone_list:
                    phone.changed_by = request.user
                    phone.save()

            if patient_form_has_changed or telephone_formset_has_changed:
                messages.success(request, _('Personal data successfully written.'))

            return finish_handling_post(request, patient.id, 0)
    else:
        telephone_formset = telephone_inlineformset(instance=patient)

    context.update({
        'patient_form': patient_form,
        'telephone_formset': telephone_formset,
        'code': patient.code
    })

    return render(request, "patient/register_personal_data.html", context)


def patient_update_social_demographic_data(request, patient, context):
    try:
        p_social_demo = SocialDemographicData.objects.get(patient_id=patient.id)
        social_demographic_form = SocialDemographicDataForm(request.POST or None, instance=p_social_demo)
    except SocialDemographicData.DoesNotExist:
        new_sdd = SocialDemographicData()
        new_sdd.patient = patient
        social_demographic_form = SocialDemographicDataForm(request.POST or None, instance=new_sdd)

    if request.method == "POST":
        if social_demographic_form.is_valid():
            if social_demographic_form.has_changed():
                new_social_demographic_data = social_demographic_form.save(commit=False)

                # Calculate social class only if all fields were filled
                if (new_social_demographic_data.tv is not None and
                        new_social_demographic_data.radio is not None and
                        new_social_demographic_data.bath is not None and
                        new_social_demographic_data.automobile is not None and
                        new_social_demographic_data.house_maid is not None and
                        new_social_demographic_data.wash_machine is not None and
                        new_social_demographic_data.dvd is not None and
                        new_social_demographic_data.refrigerator is not None and
                        new_social_demographic_data.freezer is not None and
                        new_social_demographic_data.schooling is not None):

                    new_social_demographic_data.social_class = new_social_demographic_data.calculate_social_class(
                        tv=new_social_demographic_data.tv,
                        radio=new_social_demographic_data.radio,
                        bath=new_social_demographic_data.bath,
                        car=new_social_demographic_data.automobile,
                        housemaid=new_social_demographic_data.house_maid,
                        wash_mashine=new_social_demographic_data.wash_machine,
                        dvd=new_social_demographic_data.dvd,
                        refrigerator=new_social_demographic_data.refrigerator,
                        freezer=new_social_demographic_data.freezer,
                        # If we use the object, the parameter will have the names registered in the admin interface.
                        # To avoid that, we use post data, which is a string (hopefully) containing a number from 1 to 5
                        # schooling=new_social_demographic_data.schooling)
                        schooling=request.POST['schooling'])

                else:
                    new_social_demographic_data.social_class = ""

                    # Show message only if any of the fields were filled. Nothing is shown or calculated if none of the
                    # fields were filled.
                    if (new_social_demographic_data.tv is not None or
                            new_social_demographic_data.radio is not None or
                            new_social_demographic_data.bath is not None or
                            new_social_demographic_data.automobile is not None or
                            new_social_demographic_data.house_maid is not None or
                            new_social_demographic_data.wash_machine is not None or
                            new_social_demographic_data.dvd is not None or
                            new_social_demographic_data.refrigerator is not None or
                            new_social_demographic_data.freezer is not None or
                            new_social_demographic_data.schooling is not None):
                        messages.warning(request, _('Social class was not calculated, '
                                                    'because all the necessary fields were not filled.'))

                new_social_demographic_data.changed_by = request.user
                new_social_demographic_data.save()

                messages.success(request, _('Social demographic data successfully written.'))

            return finish_handling_post(request, patient.id, 1)
        else:
            social_demographic_form.social_class = ""

    context.update({
        'social_demographic_form': social_demographic_form,
        'code': patient.code
    })

    return render(request, "patient/register_socialdemographic_data.html", context)


def patient_update_social_history(request, patient, context):
    try:
        p_social_hist = SocialHistoryData.objects.get(patient_id=patient.id)
        social_history_form = SocialHistoryDataForm(request.POST or None, instance=p_social_hist)
    except SocialHistoryData.DoesNotExist:
        new_shd = SocialHistoryData()
        new_shd.patient = patient
        social_history_form = SocialHistoryDataForm(request.POST or None, instance=new_shd)

    if request.method == "POST":
        if social_history_form.is_valid():
            if social_history_form.has_changed():
                try:
                    new_social_history_data = social_history_form.save(commit=False)
                    new_social_history_data.changed_by = request.user
                    new_social_history_data.save()
                    messages.success(request, _('Social history successfully recorded.'))
                except ValueError:
                    messages.error(request, _('The combination is not allowed.'))
            return finish_handling_post(request, patient.id, 2)
        else:
            messages.error(request, _('The combination is not allowed.'))
    context.update({
        'social_history_form': social_history_form,
        'code': patient.code
    })

    return render(request, "patient/register_social_history.html", context)


def patient_update_medical_record(request, patient, context):
    if request.method == "POST":
        return finish_handling_post(request, patient.id, 3)

    medical_record = MedicalRecordData.objects.filter(patient=patient).order_by('record_date')

    context.update({
        'medical_record': medical_record,
        'code': patient.code
    })

    return render(request, "patient/register_medical_record.html", context)


def finish_handling_post(request, patient_id, current_tab):
    if 'action' in request.POST:
        redirect_url = reverse("patient_edit", args=(patient_id,))

        if request.POST['action'] == "show_previous":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab - 1))
        elif request.POST['action'] == "show_next":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab + 1))
        elif request.POST['action'] == "change_tab":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + request.POST['nextTab'])
        elif request.POST['action'] == "more_phones":
            return HttpResponseRedirect(redirect_url + "?currentTab=0")

    redirect_url = reverse("patient_view", args=(patient_id,))
    return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))


def patient_view_personal_data(request, patient, context):
    patient_form = PatientForm(instance=patient)

    telephone_inlineformset = inlineformset_factory(Patient, Telephone, form=TelephoneForm, extra=1)
    telephone_formset = telephone_inlineformset(instance=patient)

    if not patient.name:
        patient_form.fields['anonymous'].widget.attrs['checked'] = True

    for field in patient_form.fields:
        patient_form.fields[field].widget.attrs['disabled'] = True

    for form in telephone_formset:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

    context.update({
        'code': patient.code,
        'patient_form': patient_form,
        'telephone_formset': telephone_formset
    })

    return render(request, "patient/register_personal_data.html", context)


def patient_view_social_demographic_data(request, patient, context):
    try:
        p_social_demo = SocialDemographicData.objects.get(patient_id=patient.id)
        social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)
    except SocialDemographicData.DoesNotExist:
        social_demographic_form = SocialDemographicDataForm()

    for field in social_demographic_form.fields:
        social_demographic_form.fields[field].widget.attrs['disabled'] = True

    context.update({
        'social_demographic_form': social_demographic_form,
        'code': patient.code
    })

    return render(request, "patient/register_socialdemographic_data.html", context)


def patient_view_social_history(request, patient, context):
    try:
        p_social_hist = SocialHistoryData.objects.get(patient_id=patient.id)
        social_history_form = SocialHistoryDataForm(instance=p_social_hist)
    except SocialHistoryData.DoesNotExist:
        social_history_form = SocialHistoryDataForm()

    for field in social_history_form.fields:
        social_history_form.fields[field].widget.attrs['disabled'] = True

    context.update({
        'social_history_form': social_history_form,
        'code': patient.code
    })

    return render(request, "patient/register_social_history.html", context)


def patient_view_medical_record(request, patient, context):
    medical_record = MedicalRecordData.objects.filter(patient_id=patient.id).order_by('record_date')

    context.update({
        'medical_record': medical_record,
        'code': patient.code
    })

    return render(request, "patient/register_medical_record.html", context)


def patient_view_questionnaires(request, patient, context, is_update):

    if is_update and request.method == 'POST':
        return finish_handling_post(request, patient.id, 4)

    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)
    patient_questionnaires_data_dictionary = {}
    initial_evaluation_list = Survey.objects.filter(is_initial_evaluation=True)
    language_code = request.LANGUAGE_CODE

    # First, add initial evaluation...
    for initial_evaluation in initial_evaluation_list:
        patient_questionnaires_data_dictionary[
            initial_evaluation.lime_survey_id] = {
                'is_initial_evaluation': True,
                'survey_id': initial_evaluation.pk,
                'questionnaire_title':
                    find_questionnaire_name(
                        initial_evaluation, language_code)['name'],
                'questionnaire_responses': []
            }

    # ...after, add questionnaire responses
    questionnaire_responses = \
        QuestionnaireResponse.objects.filter(patient=patient).order_by('date')

    for questionnaire_response in questionnaire_responses:
        limesurvey_id = questionnaire_response.survey.lime_survey_id
        if limesurvey_id not in patient_questionnaires_data_dictionary:
            patient_questionnaires_data_dictionary[limesurvey_id] = {
                    'is_initial_evaluation': False,
                    'survey_id': questionnaire_response.survey.pk,
                    'questionnaire_title':
                        find_questionnaire_name(
                            questionnaire_response.survey,
                            language_code)["name"],
                    'questionnaire_responses': []
                }

        properties = surveys.get_participant_properties(
            limesurvey_id, questionnaire_response.token_id)
        if properties:
            update_completed_status(
                limesurvey_id, properties['completed'],
                questionnaire_response)
            language = get_questionnaire_language(
                surveys, limesurvey_id, language_code)
            acquisitiondate_updated = update_acquisition_date(
                limesurvey_id, properties['token'],
                questionnaire_response, language)

            response_result = questionnaire_response.is_completed

            patient_questionnaires_data_dictionary[
                limesurvey_id
            ]['questionnaire_responses'].append({
                'questionnaire_response': questionnaire_response,
                'token_id': questionnaire_response.token_id,
                'completed': None if response_result is None
                else response_result != 'N' and response_result != '',
                'acquisitiondate_updated': acquisitiondate_updated
            })

    patient_questionnaires_data_list = []
    # Transforming the dictionary to a list in order to sort
    for key, dictionary in list(patient_questionnaires_data_dictionary.items()):
        dictionary['limesurvey_id'] = key
        patient_questionnaires_data_list.append(dictionary)

    # Sorting by questionnaire_title and is_initial_evaluation (reversed),
    # where is_initial_evaluation is more relevant.
    patient_questionnaires_data_list = sorted(
        patient_questionnaires_data_list,
        key=itemgetter('questionnaire_title'))
    patient_questionnaires_data_list = sorted(
        patient_questionnaires_data_list,
        key=itemgetter('is_initial_evaluation'), reverse=True)

    additional_survey_list = []
    if is_update:
        for survey in Survey.objects.exclude(
                lime_survey_id__in=[
                    item['limesurvey_id']
                    for item in patient_questionnaires_data_list
                ]):
            additional_survey_list.append({
                'id': survey.id, 'lime_survey_id': survey.lime_survey_id,
                'title': find_questionnaire_name(survey, language_code)["name"]
            })

    # Questionnaires filled in an experiment group
    questionnaires_data = []
    subject = Subject.objects.filter(patient=patient)
    subject_of_group_list = SubjectOfGroup.objects.filter(subject=subject)
    for subject_of_group in subject_of_group_list:
        experiment_questionnaire_responses = \
            ExperimentQuestionnaireResponse.objects.filter(
                subject_of_group=subject_of_group)
        for questionnaire_response in experiment_questionnaire_responses:
            component_configuration = \
                questionnaire_response.data_configuration_tree.component_configuration
            limesurvey_id = \
                component_configuration.component.questionnaire.survey.lime_survey_id

            if questionnaire_response.is_completed == 'N' \
                    or questionnaire_response.is_completed == '':
                is_completed = surveys.get_participant_properties(
                    limesurvey_id, questionnaire_response.token_id,
                    'completed') or ''
                questionnaire_response.is_completed = is_completed
                questionnaire_response.save()

            response_result = questionnaire_response.is_completed

            questionnaires_data.append({
                    'research_project_title':
                        subject_of_group.group.experiment.research_project.title,
                    'experiment_title':
                        subject_of_group.group.experiment.title,
                    'group_title': subject_of_group.group.title,
                    'questionnaire_title': find_questionnaire_name(
                            component_configuration.component.questionnaire.survey,
                        language_code)["name"],
                    'questionnaire_response': questionnaire_response,
                    'token_id': questionnaire_response.token_id,
                    'completed': None if response_result is None
                    else response_result != 'N' and response_result != ''
                })
    surveys.release_session_key()
    context.update({
        'patient_questionnaires_data_list': patient_questionnaires_data_list,
        'questionnaires_data': questionnaires_data,
        'limesurvey_available': limesurvey_available,
        'code': patient.code,
        'additional_survey_list': additional_survey_list,
    })

    return render(request, "patient/register_questionnaires.html", context)


def update_completed_status(
        limesurvey_id, is_completed, questionnaire_response):
    if questionnaire_response.is_completed == 'N' \
            or questionnaire_response.is_completed == '':
        questionnaire_response.is_completed = is_completed
        questionnaire_response.save()


def update_acquisition_date(
        limesurvey_id, token, questionnaire_response, language):
    updated = False
    if questionnaire_response.is_completed != 'N' \
            and questionnaire_response.is_completed != '':
        surveys = Questionnaires()

        responses = surveys.get_responses_by_token(
            limesurvey_id, token, language)
        if responses:
            responses_list = csv_to_list(responses)
            if responses_list[0]['acquisitiondate']:
                new_date = datetime.datetime.strptime(
                    responses_list[0]['acquisitiondate'], '%Y-%m-%d %H:%M:%S').date()
                if questionnaire_response.date != new_date:
                    questionnaire_response.date = new_date
                    questionnaire_response.save()
                    updated = True

            surveys.release_session_key()

    return updated


@login_required
@permission_required('patient.view_patient')
def search_patient(request):
    context = {'number_of_patients': Patient.objects.exclude(removed=True).count()}

    return render(request, 'patient/busca.html', context)


@login_required
def advanced_search(request):
    return render(request, 'patient/busca_avancada.html')


@login_required
def restore_patient(request, patient_id):
    patient_restored = Patient.objects.get(id=patient_id)
    patient_restored.removed = False
    patient_restored.save()

    redirect_url = reverse("patient_view", args=(patient_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('patient.view_patient')
def search_patients_ajax(request):
    patient_list = ''
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('P{1}[0-9]', search_text):
                patient_list = \
                    Patient.objects.filter(code__icontains=search_text).exclude(removed=True).order_by('code')
            elif re.match('[a-zA-Z ]+', search_text):
                patient_list = \
                    Patient.objects.filter(name__icontains=search_text).exclude(removed=True).order_by('name')
            else:
                patient_list = \
                    Patient.objects.filter(cpf__icontains=search_text).exclude(removed=True).order_by('name')

    return render_to_response('patient/ajax_search.html', {'patients': patient_list})


@login_required
@permission_required('patient.view_patient')
def patients_verify_homonym(request):
    patient_homonym = None
    if request.method == "POST":
        search_text = request.POST['search_text'].strip()
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_homonym = Patient.objects.filter(name=search_text).exclude(removed=True)
            else:
                patient_homonym = Patient.objects.filter(cpf=search_text).exclude(removed=True)
        else:
            patient_homonym = ''

    return render_to_response('patient/ajax_homonym.html', {'patient_homonym': patient_homonym})


@login_required
@permission_required('patient.view_patient')
def patients_verify_homonym_excluded(request):
    patient_homonym_excluded = None
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_homonym_excluded = Patient.objects.filter(name=search_text, removed=True)
            else:
                patient_homonym_excluded = Patient.objects.filter(cpf=search_text, removed=True)
        else:
            patient_homonym_excluded = ''

    return render_to_response('patient/ajax_homonym.html', {'patient_homonym_excluded': patient_homonym_excluded})


@login_required
@permission_required('patient.add_medicalrecorddata')
def search_cid10_ajax(request):
    cid_10_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']
        medical_record = request.POST['medical_record']
        patient_id = request.POST['patient_id']

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(
                Q(abbreviated_description__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(code__icontains=search_text)).order_by("code")

        return render_to_response(
            'patient/ajax_cid10.html', {
                'cid_10_list': cid_10_list,
                'medical_record': medical_record,
                'patient_id': patient_id
            })


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_create(
        request, patient_id, template_name='patient/medical_record.html'):
    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    return render(request, template_name, {
        'patient': patient, 'patient_id': patient_id, 'creating': True,
        'editing': True
    })


@login_required
@permission_required('patient.view_medicalrecorddata')
def medical_record_view(
        request, patient_id, record_id, template_name="patient/medical_record.html"):
    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    current_patient = get_object_or_404(Patient, pk=patient_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=record_id)

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    if medical_record:

        diagnosis_list = Diagnosis.objects.filter(
            medical_record_data=record_id).order_by('classification_of_diseases')
        complementary_exams_list = []
        for diagnosis in diagnosis_list:
            complementary_exams_list.append(ComplementaryExam.objects.filter(
                diagnosis=diagnosis.pk))

        lists_diagnosis_exams = list(
            zip(diagnosis_list, complementary_exams_list))

        return render(request, template_name, {
            'patient': patient, 'patient_id': patient_id,
            'record_id': medical_record.id, 'object_list': diagnosis_list,
            'lists_diagnosis_exams': lists_diagnosis_exams,
            'complementary_exams_list': complementary_exams_list,
            'record_date': medical_record.record_date,
            'record_responsible': medical_record.record_responsible,
            'editing': False,
            'status': status
        })


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_update(
        request, patient_id, record_id, template_name="patient/medical_record.html"):
    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    current_tab = get_current_tab(request)

    current_patient = get_object_or_404(Patient, pk=patient_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=record_id)

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    if medical_record:
        diagnosis_list = Diagnosis.objects.filter(
            medical_record_data=record_id).order_by('classification_of_diseases')
        complementary_exams_list = []

        for diagnosis in diagnosis_list:
            complementary_exams_list.append(
                ComplementaryExam.objects.filter(diagnosis=diagnosis.pk))

        lists_diagnosis_exams = list(
            zip(diagnosis_list, complementary_exams_list))

        if request.method == "POST":

            if request.POST['action'] == "finish":

                redirect_url = reverse("patient_edit", args=(patient_id, ))
                return HttpResponseRedirect(redirect_url + "?currentTab=3")

            elif request.POST['action'][0:7] == "detail-":

                diagnosis_id = int(request.POST['action'][7:])
                diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)

                diagnosis.description = \
                    request.POST['description-' + str(diagnosis_id)]
                date_text = request.POST['date-' + str(diagnosis_id)]

                try:
                    if date_text:
                        diagnosis.date = datetime.datetime.strptime(
                            date_text, _('%m/%d/%Y'))
                    else:
                        diagnosis.date = None

                    diagnosis.save()
                    messages.success(
                        request, _('Diagnosis details successfully changed.'))

                    redirect_url = reverse(
                        'medical_record_edit', args=(patient_id, record_id))
                    return HttpResponseRedirect(redirect_url + '?status=edit')

                except ValueError:
                    messages.error(
                        request, _('Incorrect date. Use format: mm/dd/yyyy'))

        return render(request, template_name, {
            'patient': patient, 'patient_id': patient_id,
            'record_id': medical_record.id, 'object_list': diagnosis_list,
            'lists_diagnosis_exams': lists_diagnosis_exams,
            'complementary_exams_list': complementary_exams_list,
            'record_date': medical_record.record_date,
            'record_responsible': medical_record.record_responsible,
            'editing': True,
            'status': status,
            'currentTab': current_tab
        })


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_delete(request, patient_id, record_id):
    medical_record = MedicalRecordData.objects.get(pk=record_id)
    medical_record.delete()
    messages.success(request, _('Medical evaluation successfully deleted.'))

    redirect_url = reverse("patient_edit", args=(patient_id,))
    return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=3")


@login_required
@permission_required('patient.add_medicalrecorddata')
def diagnosis_create(request, patient_id, medical_record_id, cid10_id):
    medical_record = MedicalRecordData.objects.get(pk=medical_record_id)
    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    if Diagnosis.objects.filter(
            medical_record_data=medical_record).filter(
        classification_of_diseases=cid10):
        messages.warning(
            request, _('Diagnosis has already exist in this medical assessment.'))
    else:
        diagnosis = Diagnosis(
            medical_record_data=medical_record,
            classification_of_diseases=cid10)
        diagnosis.save()

    redirect_url = reverse(
        'medical_record_edit', args=(patient_id, medical_record_id,))

    return HttpResponseRedirect(redirect_url + '?status=edit&currentTab=3')


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_create_diagnosis_create(request, patient_id, cid10_id):
    current_patient = Patient.objects.get(id=patient_id)

    new_medical_record = MedicalRecordData()
    new_medical_record.patient = current_patient
    new_medical_record.record_responsible = request.user
    new_medical_record.save()

    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    diagnosis = Diagnosis(
        medical_record_data=new_medical_record, classification_of_diseases=cid10)
    diagnosis.save()

    redirect_url = reverse(
        'medical_record_edit', args=(patient_id, new_medical_record.id,))
    return HttpResponseRedirect(redirect_url + '?status=edit&currentTab=3')


@login_required
@permission_required('patient.add_medicalrecorddata')
def diagnosis_delete(request, patient_id, diagnosis_id):
    exams = ComplementaryExam.objects.filter(diagnosis=diagnosis_id)
    if exams:
        messages.error(
            request, _('Diagnosis can not be deleted. You must delete exams before.'))
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
    else:
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
        diagnosis.delete()
        messages.success(request, _('Diagnosis successfully deleted.'))

    medical_record_id = diagnosis.medical_record_data_id
    medical_record = MedicalRecordData.objects.get(pk=medical_record_id)
    if medical_record.diagnosis_set.count() == 0:
        medical_record.delete()
        redirect_url = reverse('medical_record_new', args=(patient_id, ))
    else:
        redirect_url = reverse(
            'medical_record_edit', args=(patient_id, medical_record_id, ))

    return HttpResponseRedirect(redirect_url + '?status=edit&currentTab=3')


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_create(
        request, patient_id, record_id, diagnosis_id,
        template_name="patient/exams.html"):
    form = ComplementaryExamForm(request.POST or None)

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    new_medical_record = False
    if 'mr' in request.GET:
        new_medical_record = True

    diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    if request.method == "POST":
        file_form = ExamFileForm(request.POST, request.FILES)

        if 'content' in request.FILES:
            if form.is_valid():
                new_complementary_exam = form.save(commit=False)
                new_complementary_exam.diagnosis = diagnosis
                new_complementary_exam.save()

                if file_form.is_valid():
                    new_file_data = file_form.save(commit=False)
                    new_file_data.exam = new_complementary_exam
                    new_file_data.save()
                    messages.success(request, _('Exam successfully saved.'))

                if new_medical_record:
                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                else:
                    redirect_url = reverse("medical_record_view", args=(patient_id, record_id, ))

                return HttpResponseRedirect(redirect_url + "?status=" + status)

        else:
            messages.error(request, _('It is not possible to save exam without files.'))

    else:
        file_form = ExamFileForm(request.POST)

    return render(request, template_name,
                  {'viewing': False,
                   'creating': True,
                   'complementary_exam_form': form,
                   'patient_id': patient_id,
                   'record_id': record_id,
                   'patient': patient,
                   'file_form': file_form,
                   'status': status,
                   'new_medical_record': new_medical_record}, )


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_edit(request, patient_id, record_id, exam_id, template_name="patient/exams.html"):
    current_patient = Patient.objects.get(id=patient_id)
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    new_medical_record = False
    if 'mr' in request.GET:
        new_medical_record = True

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    if complementary_exam:
        complementary_exam_form = ComplementaryExamForm(request.POST or None, instance=complementary_exam)
        exam_file_list = ExamFile.objects.filter(exam=exam_id)
        length = exam_file_list.__len__()

        if request.method == "POST":

            file_form = ExamFileForm(request.POST, request.FILES)

            if 'content' in request.FILES or length > 0:
                if complementary_exam_form.is_valid():
                    complementary_exam_form.save()

                    if file_form.is_valid():
                        new_file_data = file_form.save(commit=False)
                        new_file_data.exam = complementary_exam
                        new_file_data.save()

                    messages.success(request, _('Exam successfully saved.'))
                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                    return HttpResponseRedirect(redirect_url + "?status=" + status)

            else:
                messages.error(request, _('It is not possible to save exam without files.'))

        else:
            file_form = ExamFileForm(request.POST)

        return render(request, template_name,
                      {'viewing': False,
                       'creating': False,
                       'complementary_exam_form': complementary_exam_form,
                       'exam_file_list': exam_file_list,
                       'length': length,
                       'patient_id': patient_id,
                       'record_id': record_id,
                       'patient': patient,
                       'file_form': file_form,
                       'status': status,
                       'new_medical_record': new_medical_record})


@login_required
@permission_required('patient.view_medicalrecorddata')
def exam_view(request, patient_id, record_id, exam_id, template_name="patient/exams.html"):
    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    current_patient = Patient.objects.get(id=patient_id)
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)
    complementary_exam_form = ComplementaryExamForm(instance=complementary_exam)

    for field in complementary_exam_form.fields:
        complementary_exam_form.fields[field].widget.attrs['disabled'] = True

    try:
        exam_file_list = ExamFile.objects.filter(exam=exam_id)
    except ExamFile.DoesNotExist:
        exam_file_list = None

    if current_patient.name:
        patient = current_patient.name
    else:
        patient = current_patient.code

    return render(request, template_name,
                  {'viewing': True,
                   'creating': False,
                   'complementary_exam_form': complementary_exam_form,
                   'exam_file_list': exam_file_list,
                   'patient_id': patient_id,
                   'record_id': record_id,
                   'patient': patient,
                   'status': status})


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_delete(request, patient_id, record_id, exam_id):

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    new_medical_record = False
    if 'mr' in request.GET:
        new_medical_record = True

    complementary_exam = get_object_or_404(ComplementaryExam, pk=exam_id)

    if complementary_exam:
        complementary_exam.delete()
        messages.success(request, _('Exam successfully deleted.'))

    if new_medical_record:
        redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
    else:
        redirect_url = reverse("medical_record_view", args=(patient_id, record_id, ))

    return HttpResponseRedirect(redirect_url + "?status=" + status)


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_file_delete(request, exam_file_id):

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    new_medical_record = False
    if 'mr' in request.GET:
        new_medical_record = True

    exam_file = get_object_or_404(ExamFile, pk=exam_file_id)
    exam_file.delete()
    messages.success(request, _('Attachment successfully deleted.'))

    complementary_exam = get_object_or_404(ComplementaryExam, pk=exam_file.exam_id)
    diagnosis = get_object_or_404(Diagnosis, pk=complementary_exam.diagnosis_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=diagnosis.medical_record_data_id)

    redirect_url = reverse("exam_edit",
                           args=(
                               medical_record.patient_id,
                               diagnosis.medical_record_data_id,
                               complementary_exam.pk))
    return HttpResponseRedirect(redirect_url + "?status=" + status + ("&mr=new" if new_medical_record else ""))


def get_origin(request):
    origin = '0'

    if 'origin' in request.GET:
        origin = request.GET['origin']
    else:
        if 'origin' in request.POST:
            origin = request.POST['origin']

    return origin

@login_required
@permission_required('patient.view_questionnaireresponse')
def questionnaire_response_view(
        request, questionnaire_response_id,
        template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_response = get_object_or_404(
        QuestionnaireResponse, pk=questionnaire_response_id)

    if questionnaire_response.is_completed == 'N' or questionnaire_response.is_completed == "":
        surveys = Questionnaires()
        is_completed = surveys.get_participant_properties(
            questionnaire_response.survey.lime_survey_id,
            questionnaire_response.token_id,
            "completed") or ""
        questionnaire_response.is_completed = is_completed
        questionnaire_response.save()
        surveys.release_session_key()

    survey_completed = (questionnaire_response.is_completed != "N")

    questionnaire_response_form = QuestionnaireResponseForm(None, instance=questionnaire_response)

    showing = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            if request.user.has_perm('patient.delete_questionnaireresponse'):
                surveys = Questionnaires()
                result = surveys.delete_participants(
                    questionnaire_response.survey.lime_survey_id,
                    [questionnaire_response.token_id])
                surveys.release_session_key()

                can_delete = False

                if str(questionnaire_response.token_id) in result:
                    result = result[str(questionnaire_response.token_id)]
                    if result == 'Deleted' or result == 'Invalid token ID':
                        can_delete = True
                else:
                    if 'status' in result and result['status'] == \
                            'Error: Invalid survey ID':
                        can_delete = True

                if can_delete:
                    questionnaire_response.delete()
                    messages.success(request, _('Fill deleted successfully'))
                else:
                    messages.error(request, _("Error trying to delete"))

                redirect_url = reverse(
                    "patient_edit",
                    args=(questionnaire_response.patient.id,)) + "?currentTab=4"
                return HttpResponseRedirect(redirect_url)
            else:
                raise PermissionDenied

    origin = get_origin(request)

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    response_is_reused_in_experiment = False
    # steps that use this survey
    questionnaire_component_list = Questionnaire.objects.filter(survey=questionnaire_response.survey)
    if questionnaire_component_list:
        # experiment questionnaire responses that reused this token
        response_is_reused_in_experiment = \
            ExperimentQuestionnaireResponse.objects.filter(
                token_id=questionnaire_response.token_id,
                data_configuration_tree__component_configuration__component__in=questionnaire_component_list).exists()

    survey_title_key = \
        request.LANGUAGE_CODE + "-" + str(questionnaire_response.survey.lime_survey_id) + \
        "-" + str(questionnaire_response.token_id) + "_survey_title_participant"
    groups_of_questions_key = \
        request.LANGUAGE_CODE + "-" + str(questionnaire_response.survey.lime_survey_id) + \
        "-" + str(questionnaire_response.token_id) + "_group_of_questions_participant"

    survey_title = cache.get(survey_title_key)
    groups_of_questions = cache.get(groups_of_questions_key)

    if not survey_title or not groups_of_questions:
        survey_title, groups_of_questions = get_questionnaire_responses(
            request.LANGUAGE_CODE, questionnaire_response.survey.lime_survey_id,
            questionnaire_response.token_id, request)

        cache.set(survey_title_key, survey_title)
        cache.set(groups_of_questions_key, groups_of_questions)

    context = {
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": None,
        "questionnaire_response": questionnaire_response,
        "survey_title": survey_title,
        "questionnaire_responsible": questionnaire_response.questionnaire_responsible.username,
        "creating": False,
        "completed": survey_completed,
        "origin": origin,
        "patient": questionnaire_response.patient,
        "questionnaire": questionnaire_response.survey,
        "groups_of_questions": groups_of_questions,
        "questionnaire_title": survey_title,
        "showing": showing,
        "updating": True,
        "status": status,
        "response_is_reused_in_experiment": response_is_reused_in_experiment,
        # This is related to permission to change an experiment, which is
        # not the case here.
        "can_change": True
    }

    return render(request, template_name, context)


@login_required
# TODO: associate the right permission
# @permission_required('patient.add_medicalrecorddata')
def questionnaire_response_create(
        request, patient_id, survey_id,
        template_name="experiment/subject_questionnaire_response_form.html"):
    patient = get_object_or_404(Patient, pk=patient_id)
    survey = get_object_or_404(Survey, pk=survey_id)

    surveys = Questionnaires()
    language = get_questionnaire_language(
        surveys, survey.lime_survey_id, request.LANGUAGE_CODE)
    survey_title = surveys.get_survey_title(survey.lime_survey_id, language)
    surveys.release_session_key()

    fail = None
    redirect_url = None
    questionnaire_response_id = None
    showing = False

    questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)

    if request.method == "POST":
        if request.POST['action'] == "save":
            redirect_url, questionnaire_response_id = \
                questionnaire_response_start_fill_questionnaire(request, patient_id, survey)

            if not redirect_url:
                fail = True
            else:
                fail = False

                showing = True
                for field in questionnaire_response_form.fields:
                    questionnaire_response_form.fields[
                        field
                    ].widget.attrs['disabled'] = True

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_response_form": questionnaire_response_form,
        "survey_title": survey_title,
        "questionnaire_responsible": request.user.get_username(),
        "creating": True,
        "origin": origin,
        "patient": patient,
        "showing": showing,
        "status": "edit",
        "completed": False,
        "can_change": True
    }

    return render(request, template_name, context)


@login_required
@permission_required('patient.change_questionnaireresponse')
def questionnaire_response_update(
        request, questionnaire_response_id,
        template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_response = get_object_or_404(
        QuestionnaireResponse, pk=questionnaire_response_id)

    surveys = Questionnaires()
    language = get_questionnaire_language(
        surveys, questionnaire_response.survey.lime_survey_id,
        request.LANGUAGE_CODE)
    survey_title = surveys.get_survey_title(
        questionnaire_response.survey.lime_survey_id, language)
    survey_completed = surveys.get_participant_properties(
        questionnaire_response.survey.lime_survey_id,
        questionnaire_response.token_id, "completed") != "N"
    surveys.release_session_key()

    patient = get_object_or_404(Patient, pk=questionnaire_response.patient_id)

    questionnaire_response_form = QuestionnaireResponseForm(
        None, instance=questionnaire_response)

    fail = None
    redirect_url = None
    questionnaire_response_id = None
    showing = True

    questionnaire = questionnaire_response.survey
    questionnaire_title = survey_title

    if request.method == "POST":
        if request.POST['action'] == "save":
            redirect_url = get_limesurvey_response_url(questionnaire_response)

            fail = True if not redirect_url else False

        elif request.POST['action'] == "remove":
            if request.user.has_perm('patient.delete_questionnaireresponse'):
                surveys = Questionnaires()
                result = surveys.delete_participants(
                    questionnaire_response.survey.lime_survey_id,
                    [questionnaire_response.token_id])
                surveys.release_session_key()

                can_delete = False

                if str(questionnaire_response.token_id) in result:
                    result = result[str(questionnaire_response.token_id)]
                    if result == 'Deleted' or result == 'Invalid token ID':
                        can_delete = True
                else:
                    if 'status' in result and result['status'] == \
                            'Error: Invalid survey ID':
                        can_delete = True

                if can_delete:
                    questionnaire_response.delete()
                    messages.success(request, _('Fill deleted successfully'))
                else:
                    messages.error(request, _("Error trying to delete"))

                redirect_url = reverse(
                    "patient_edit", args=(patient.id,)) + "?currentTab=4"
                return HttpResponseRedirect(redirect_url)
            else:
                raise PermissionDenied

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": None,
        "questionnaire_response": questionnaire_response,
        "survey_title": survey_title,
        "questionnaire_responsible": request.user.get_username(),
        "creating": False,
        "subject": None,
        "completed": survey_completed,
        "group": None,
        "origin": origin,
        "questionnaires_list": None,
        "patient": patient,
        "questionnaire": questionnaire,
        "questionnaire_title": questionnaire_title,
        "showing": showing,
        "updating": True,
        "status": request.GET.get('status', ''),
        "can_change": True
    }

    return render(request, template_name, context)


def questionnaire_response_start_fill_questionnaire(request, patient_id, survey):

    questionnaire_response_form = QuestionnaireResponseForm(request.POST)

    if questionnaire_response_form.is_valid():

        questionnaire_response = questionnaire_response_form.save(commit=False)

        questionnaire_lime_survey = Questionnaires()

        patient = get_object_or_404(Patient, pk=patient_id)

        if not questionnaire_lime_survey.survey_has_token_table(survey.lime_survey_id):
            messages.warning(request,
                             _('Not available filling - tokens table not started'))
            return None, None

        if questionnaire_lime_survey.get_survey_properties(survey.lime_survey_id, 'active') == 'N':
            messages.warning(request,
                             _('Not available filling - questionnaire not active'))
            return None, None

        if not check_required_fields(questionnaire_lime_survey, survey.lime_survey_id):
            messages.warning(
                request, _('Not available filling - questionnaire does not contain standard fields'))
            return None, None

        result = questionnaire_lime_survey.add_participant(survey.lime_survey_id)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(request,
                             _('Failed to generate token to answer the questionnaire. '
                               'Make sure the questionnaire is active'))
            return None, None

        questionnaire_response.patient = patient
        questionnaire_response.survey = survey
        questionnaire_response.token_id = result['tid']
        questionnaire_response.questionnaire_responsible = request.user
        questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(questionnaire_response)

        return redirect_url, questionnaire_response.pk
    else:
        return None, None


def check_required_fields(surveys, lime_survey_id):
    """
    Verify if questionnaire have right identification questions
    and question types
    """

    fields_to_validate = {
        'responsibleid': {'type': 'N', 'found': False},
        'acquisitiondate': {'type': 'D', 'found': False},
        'subjectid': {'type': 'N', 'found': False},
    }

    validated_quantity = 0
    error = False

    groups = surveys.list_groups(lime_survey_id)

    if 'status' not in groups:

        for group in groups:
            question_list = surveys.list_questions_ids(lime_survey_id, group['id']['gid'])
            for question in question_list:
                question_properties = surveys.get_question_properties(question, None)
                if question_properties['title'] in fields_to_validate:
                    field = fields_to_validate[question_properties['title']]
                    if not field['found']:
                        field['found'] = True
                        if field['type'] == question_properties['type']:
                            validated_quantity += 1
                        else:
                            error = True
                if error or validated_quantity == len(fields_to_validate):
                    break
            if error or validated_quantity == len(fields_to_validate):
                break

    return validated_quantity == len(fields_to_validate)


def get_limesurvey_response_url(questionnaire_response):
    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(
        questionnaire_response.survey.lime_survey_id,
        questionnaire_response.token_id, "token")

    redirect_url = \
        '%s/index.php/%s/token/%s/responsibleid/%s/acquisitiondate/%s/' \
        'subjectid/%s/newtest/Y' % (
            settings.LIMESURVEY['URL_WEB'],
            questionnaire_response.survey.lime_survey_id,
            token,
            str(questionnaire_response.questionnaire_responsible.id),
            questionnaire_response.date.strftime('%m-%d-%Y'),
            str(questionnaire_response.patient.id))

    questionnaire_lime_survey.release_session_key()

    return redirect_url
