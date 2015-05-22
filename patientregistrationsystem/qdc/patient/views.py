# coding=utf-8
import datetime
from functools import partial
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404

from django.conf import settings

from patient.models import Patient, Telephone, SocialDemographicData, SocialHistoryData, MedicalRecordData, \
    ClassificationOfDiseases, Diagnosis, ExamFile, ComplementaryExam
from patient.forms import PatientForm, TelephoneForm, SocialDemographicDataForm, SocialHistoryDataForm, \
    ComplementaryExamForm, ExamFileForm
from patient.quiz_widget import SelectBoxCountriesDisabled, SelectBoxStateDisabled

from experiment.models import Subject, Experiment, Group, SubjectOfGroup, \
    QuestionnaireConfiguration, QuestionnaireResponse, Questionnaire, PatientQuestionnaireResponse
from experiment.abc_search_engine import Questionnaires
from experiment.forms import QuestionnaireResponseForm, PatientQuestionnaireResponseForm

# pylint: disable=E1101
# pylint: disable=E1103

permission_required = partial(permission_required, raise_exception=True)


@login_required
@permission_required('patient.add_patient')
def patient_create(request, template_name="patient/register_personal_data.html"):
    patient_form = PatientForm(request.POST or None)

    TelephoneFormSet = inlineformset_factory(Patient, Telephone, form=TelephoneForm)

    if request.method == "POST":
        patient_form_is_valid = patient_form.is_valid()

        telephone_formset = TelephoneFormSet(request.POST, request.FILES)
        telephone_formset_is_valid = telephone_formset.is_valid()

        if patient_form_is_valid and telephone_formset_is_valid:
            new_patient = patient_form.save(commit=False)

            if not new_patient.cpf:
                new_patient.cpf = None

            new_patient.changed_by = request.user
            new_patient.save()

            new_phone_list = telephone_formset.save(commit=False)

            for phone in new_phone_list:
                phone.changed_by = request.user
                phone.patient_id = new_patient.id
                phone.save()

            messages.success(request, 'Dados pessoais gravados com sucesso.')
            return finish_handling_post(request, new_patient.id, 0)
        else:
            if request.POST['cpf']:
                patient_found = Patient.objects.filter(cpf=request.POST['cpf'])

                if patient_found:
                    if patient_found[0].removed:
                        patient_form.errors['cpf'][0] = "Já existe paciente removido com este CPF."
                    else:
                        patient_form.errors['cpf'][0] = "Já existe paciente cadastrado com este CPF."
    else:
        telephone_formset = TelephoneFormSet()

    context = {
        'patient_form': patient_form,
        'telephone_formset': telephone_formset,
        'editing': True,
        'inserting': True,
        'currentTab': '0'}

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
            return patient_update_social_demographic_data(request, patient, context)
        elif current_tab == '2':
            return patient_update_social_history(request, patient, context)
        elif current_tab == '3':
            return patient_update_medical_record(request, patient, context)
        else: # current_tab == '4':
            return patient_update_questionnaires(request, patient, context)


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

    TelephoneFormSet = inlineformset_factory(Patient, Telephone, form=TelephoneForm)

    if request.method == "POST":
        patient_form_is_valid = patient_form.is_valid()

        telephone_formset = TelephoneFormSet(request.POST, request.FILES, instance=patient)
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
                messages.success(request, 'Dados pessoais gravados com sucesso.')

            return finish_handling_post(request, patient.id, 0)
    else:
        telephone_formset = TelephoneFormSet(instance=patient)

    context.update({
        'patient_form': patient_form,
        'telephone_formset': telephone_formset})

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
                        # To avoid that, we use post data, which is a string (hopefully) containing a number from 1 to 5.
                        # schooling=new_social_demographic_data.schooling)
                        schooling=request.POST['schooling'])

                else:
                    new_social_demographic_data.social_class = None

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
                        messages.warning(request, 'Classe Social não calculada, pois nem todos os campos necessários '
                                                  'para o cálculo foram preenchidos.')

                new_social_demographic_data.changed_by = request.user
                new_social_demographic_data.save()

                messages.success(request, 'Dados sociodemográficos gravados com sucesso.')

            return finish_handling_post(request, patient.id, 1)

    context.update({
        'social_demographic_form': social_demographic_form})

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
                new_social_history_data = social_history_form.save(commit=False)
                new_social_history_data.changed_by = request.user
                new_social_history_data.save()
                messages.success(request, 'História social gravada com sucesso.')

            return finish_handling_post(request, patient.id, 2)

    context.update({
        'social_history_form': social_history_form})

    return render(request, "patient/register_social_history.html", context)


def patient_update_medical_record(request, patient, context):
    if request.method == "POST":
        return finish_handling_post(request, patient.id, 3)

    medical_record = MedicalRecordData.objects.filter(patient=patient).order_by('record_date')

    context.update({
        'medical_record': medical_record})

    return render(request, "patient/register_medical_record.html", context)


def patient_update_questionnaires(request, patient, context):
    if request.method == "POST":
        return finish_handling_post(request, patient.id, 4)

    questionnaires_data = []

    # TODO Sort the questionnaires somehow.

    surveys = Questionnaires()

    limesurvey_available = check_limesurvey_access(request, surveys)

    patient_questionnaires_data = []
    patient_questionnaire_response_list = PatientQuestionnaireResponse.objects.filter(patient=patient)

    for patient_questionnaire_response in patient_questionnaire_response_list:

        response_result = surveys.get_participant_properties(
            patient_questionnaire_response.questionnaire.lime_survey_id,
            patient_questionnaire_response.token_id,
            "completed")

        patient_questionnaires_data.append(
            {
                'questionnaire_title':
                surveys.get_survey_title(patient_questionnaire_response.questionnaire.lime_survey_id),
                'questionnaire_response':
                patient_questionnaire_response,
                'completed':
                None if response_result is None else response_result != "N" and response_result != ""
            }
        )

    subject = Subject.objects.filter(patient=patient)
    subject_of_group_list = SubjectOfGroup.objects.filter(subject=subject)

    for subject_of_group in subject_of_group_list:
        group = get_object_or_404(Group, id=subject_of_group.group.id)
        experiment = get_object_or_404(Experiment, id=group.experiment.id)
        questionnaire_configuration_list = QuestionnaireConfiguration.objects.filter(group=group)

        for questionnaire_configuration in questionnaire_configuration_list:
            questionnaire_response_list = QuestionnaireResponse.objects.filter(subject_of_group=subject_of_group).\
                filter(questionnaire_configuration=questionnaire_configuration)

            for questionnaire_response in questionnaire_response_list:

                response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                     questionnaire_response.token_id,
                                                                     "completed")
                questionnaires_data.append({
                    'research_project_title': experiment.research_project.title,
                    'experiment_title': experiment.title,
                    'group_title': group.title,
                    'questionnaire_title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
                    'questionnaire_response': questionnaire_response,
                    'completed': None if response_result is None
                    else response_result != "N" and response_result != ""

                })

    surveys.release_session_key()

    context.update({
        'patient_questionnaires_data': patient_questionnaires_data,
        'questionnaires_data': questionnaires_data,
        'limesurvey_available': limesurvey_available})

    return render(request, "patient/register_questionnaires.html", context)


def finish_handling_post(request, patient_id, currentTab):
    if 'action' in request.POST:
        redirect_url = reverse("patient_edit", args=(patient_id,))

        if request.POST['action'] == "show_previous":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(currentTab - 1))
        elif request.POST['action'] == "show_next":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(currentTab + 1))
        elif request.POST['action'] == "change_tab":
            return HttpResponseRedirect(redirect_url + "?currentTab=" + request.POST['nextTab'])
        elif request.POST['action'] == "more_phones":
            return HttpResponseRedirect(redirect_url + "?currentTab=0")

    redirect_url = reverse("patient_view", args=(patient_id,))
    return HttpResponseRedirect(redirect_url + "?currentTab=" + str(currentTab))


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
                return HttpResponseRedirect(redirect_url + "?currentTab=" + str(int(current_tab) - 1))
            elif request.POST['action'] == "show_next":
                redirect_url = reverse("patient_view", args=(patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + str(int(current_tab) + 1))
            else:
                redirect_url = reverse("patient_edit", args=(patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + current_tab)

        return HttpResponseRedirect(redirect_url)

    if patient and not patient.removed:
        context = {
            'editing': False,
            'currentTab': current_tab,
            'patient_id': patient_id}

        if current_tab == '0':
            return patient_view_personal_data(request, patient, context)
        elif current_tab == '1':
            return patient_view_social_demographic_data(request, patient, context)
        elif current_tab == '2':
            return patient_view_social_history(request, patient, context)
        elif current_tab == '3':
            return patient_view_medical_record(request, patient, context)
        else: # current_tab == '4':
            return patient_view_questionnaires(request, patient, context)


def patient_view_personal_data(request, patient, context):
    patient_form = PatientForm(instance=patient)

    TelephoneFormSet = inlineformset_factory(Patient, Telephone, form=TelephoneForm, extra=1)
    telephone_formset = TelephoneFormSet(instance=patient)

    for field in patient_form.fields:
        patient_form.fields[field].widget.attrs['disabled'] = True

    for form in telephone_formset:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

    patient_form.fields['country'].widget = SelectBoxCountriesDisabled(
        attrs={'id': 'id_country_state_address', 'data-flags': 'true', 'disabled': 'true'})
    patient_form.fields['state'].widget = SelectBoxStateDisabled(
        attrs={'data-country': 'id_country_state_address', 'id': 'id_chosen_state', 'disabled': 'true'})

    context.update({
        'patient_form': patient_form,
        'telephone_formset': telephone_formset})

    return render(request, "patient/register_personal_data.html", context)


def patient_view_social_demographic_data(request, patient, context):
    try:
        p_social_demo = SocialDemographicData.objects.get(patient_id=patient.id)
        social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)
    except SocialDemographicData.DoesNotExist:
        social_demographic_form = SocialDemographicDataForm()

    social_demographic_form.fields['citizenship'].widget = SelectBoxCountriesDisabled(
        attrs={'id': 'id_chosen_country', 'data-flags': 'true', 'disabled': 'true'})

    for field in social_demographic_form.fields:
        social_demographic_form.fields[field].widget.attrs['disabled'] = True

    context.update({
        'social_demographic_form': social_demographic_form})

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
        'social_history_form': social_history_form})

    return render(request, "patient/register_social_history.html", context)


def patient_view_medical_record(request, patient, context):
    medical_record = MedicalRecordData.objects.filter(patient_id=patient.id).order_by('record_date')

    context.update({
        'medical_record': medical_record})

    return render(request, "patient/register_medical_record.html", context)


def check_limesurvey_access(request, surveys):
    limesurvey_available = True
    if not surveys.session_key:
        limesurvey_available = False
        messages.warning(request, "LimeSurvey indisponível. Sistema funcionando parcialmente.")

    return limesurvey_available


def patient_view_questionnaires(request, patient, context):

    surveys = Questionnaires()

    limesurvey_available = check_limesurvey_access(request, surveys)

    patient_questionnaires_data = []
    patient_questionnaire_response_list = PatientQuestionnaireResponse.objects.filter(patient=patient)

    for patient_questionnaire_response in patient_questionnaire_response_list:

        response_result = surveys.get_participant_properties(
            patient_questionnaire_response.questionnaire.lime_survey_id,
            patient_questionnaire_response.token_id,
            "completed")

        patient_questionnaires_data.append(
            {
                'questionnaire_title':
                surveys.get_survey_title(patient_questionnaire_response.questionnaire.lime_survey_id),

                'questionnaire_response':
                patient_questionnaire_response,

                'completed':
                None if response_result is None else response_result != "N" and response_result != ""
            }
        )

    questionnaires_data = []
    subject = Subject.objects.filter(patient=patient)
    subject_of_group_list = SubjectOfGroup.objects.filter(subject=subject)

    for subject_of_group in subject_of_group_list:
        group = get_object_or_404(Group, id=subject_of_group.group.id)
        experiment = get_object_or_404(Experiment, id=group.experiment.id)
        questionnaire_configuration_list = QuestionnaireConfiguration.objects.filter(group=group)

        for questionnaire_configuration in questionnaire_configuration_list:
            questionnaire_response_list = QuestionnaireResponse.objects.filter(subject_of_group=subject_of_group). \
                filter(questionnaire_configuration=questionnaire_configuration)

            for questionnaire_response in questionnaire_response_list:

                response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                     questionnaire_response.token_id,
                                                                     "completed")
                questionnaires_data.append(
                    {
                        'research_project_title': experiment.research_project.title,
                        'experiment_title': experiment.title,
                        'group_title': group.title,
                        'questionnaire_title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
                        'questionnaire_response': questionnaire_response,
                        'completed': None if response_result is None
                        else response_result != "N" and response_result != ""
                    }
                )

    surveys.release_session_key()

    context.update({
        'patient_questionnaires_data': patient_questionnaires_data,
        'questionnaires_data': questionnaires_data,
        'limesurvey_available': limesurvey_available})

    return render(request, "patient/register_questionnaires.html", context)

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
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = Patient.objects.filter(name__icontains=search_text).exclude(removed=True).order_by('name')
            else:
                patient_list = Patient.objects.filter(cpf__icontains=search_text).exclude(removed=True).order_by('name')

    return render_to_response('patient/ajax_search.html', {'patients': patient_list})


@login_required
@permission_required('patient.view_patient')
def patients_verify_homonym(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
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
            cid_10_list = ClassificationOfDiseases.objects.filter(Q(abbreviated_description__icontains=search_text) |
                                                                  Q(description__icontains=search_text))

        return render_to_response('patient/ajax_cid10.html', {'cid_10_list': cid_10_list,
                                                              'medical_record': medical_record,
                                                              'patient_id': patient_id})


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_create(request, patient_id, template_name='patient/medical_record.html'):
    current_patient = get_object_or_404(Patient, pk=patient_id)

    return render(request, template_name,
                  {'name_patient': current_patient.name,
                   'patient_id': patient_id,
                   'creating': True,
                   'editing': True})


@login_required
@permission_required('patient.view_medicalrecorddata')
def medical_record_view(request, patient_id, record_id, template_name="patient/medical_record.html"):
    status_mode = request.GET['status']

    current_patient = get_object_or_404(Patient, pk=patient_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=record_id)

    if medical_record:

        diagnosis_list = Diagnosis.objects.filter(medical_record_data=record_id).order_by('classification_of_diseases')
        complementary_exams_list = []
        for diagnosis in diagnosis_list:
            complementary_exams_list.append(ComplementaryExam.objects.filter(diagnosis=diagnosis.pk))

        lists_diagnosis_exams = zip(diagnosis_list, complementary_exams_list)

        return render(request, template_name,
                      {'name_patient': current_patient.name,
                       'patient_id': patient_id,
                       'record_id': medical_record.id,
                       'object_list': diagnosis_list,
                       'lists_diagnosis_exams': lists_diagnosis_exams,
                       'complementary_exams_list': complementary_exams_list,
                       'record_date': medical_record.record_date,
                       'record_responsible': medical_record.record_responsible,
                       'editing': False,
                       'status_mode': status_mode})


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_update(request, patient_id, record_id, template_name="patient/medical_record.html"):
    status_mode = request.GET['status']
    current_tab = get_current_tab(request)

    current_patient = get_object_or_404(Patient, pk=patient_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=record_id)

    if medical_record:
        diagnosis_list = Diagnosis.objects.filter(medical_record_data=record_id).order_by('classification_of_diseases')
        complementary_exams_list = []

        for diagnosis in diagnosis_list:
            complementary_exams_list.append(ComplementaryExam.objects.filter(diagnosis=diagnosis.pk))

        lists_diagnosis_exams = zip(diagnosis_list, complementary_exams_list)

        if request.method == "POST":

            if request.POST['action'] == "finish":

                redirect_url = reverse("patient_edit", args=(patient_id, ))
                return HttpResponseRedirect(redirect_url + "?currentTab=3")

            elif request.POST['action'][0:7] == "detail-":

                diagnosis_id = int(request.POST['action'][7:])
                diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)

                diagnosis.description = request.POST['description-' + str(diagnosis_id)]
                date_text = request.POST['date-' + str(diagnosis_id)]

                try:
                    if date_text:
                        diagnosis.date = datetime.datetime.strptime(date_text, '%d/%m/%Y')
                    else:
                        diagnosis.date = None

                    diagnosis.save()
                    messages.success(request, 'Detalhes do diagnóstico alterados com sucesso.')

                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id))
                    return HttpResponseRedirect(redirect_url + "?status=edit")

                except ValueError:
                    messages.error(request, "Data incorreta. Utilize o formato dd/mm/yyyy.")

        return render(request, template_name,
                      {'name_patient': current_patient.name,
                       'patient_id': patient_id,
                       'record_id': medical_record.id,
                       'object_list': diagnosis_list,
                       'lists_diagnosis_exams': lists_diagnosis_exams,
                       'complementary_exams_list': complementary_exams_list,
                       'record_date': medical_record.record_date,
                       'record_responsible': medical_record.record_responsible,
                       'editing': True,
                       'status_mode': status_mode,
                       'currentTab': current_tab})


@login_required
@permission_required('patient.add_medicalrecorddata')
def diagnosis_create(request, patient_id, medical_record_id, cid10_id):
    medical_record = MedicalRecordData.objects.get(pk=medical_record_id)
    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    if Diagnosis.objects.filter(medical_record_data=medical_record).filter(classification_of_diseases=cid10):
        messages.warning(request, 'Diagnóstico já existente nesta avaliação médica.')
    else:
        diagnosis = Diagnosis(medical_record_data=medical_record, classification_of_diseases=cid10)
        diagnosis.save()

    redirect_url = reverse("medical_record_edit", args=(patient_id, medical_record_id,))
    return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=3")


@login_required
@permission_required('patient.add_medicalrecorddata')
def medical_record_create_diagnosis_create(request, patient_id, cid10_id):
    current_patient = Patient.objects.get(id=patient_id)

    new_medical_record = MedicalRecordData()
    new_medical_record.patient = current_patient
    new_medical_record.record_responsible = request.user
    new_medical_record.save()

    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    diagnosis = Diagnosis(medical_record_data=new_medical_record, classification_of_diseases=cid10)
    diagnosis.save()

    redirect_url = reverse("medical_record_edit", args=(patient_id, new_medical_record.id,))
    return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=3")


@login_required
@permission_required('patient.add_medicalrecorddata')
def diagnosis_delete(request, patient_id, diagnosis_id):
    exams = ComplementaryExam.objects.filter(diagnosis=diagnosis_id)
    if exams:
        messages.error(request, 'Diagnóstico não pode ser removido. Remova os exames antes.')
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
    else:
        diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
        diagnosis.delete()
        messages.success(request, 'Diagnóstico removido com sucesso.')

    medical_record_id = diagnosis.medical_record_data_id
    redirect_url = reverse("medical_record_edit", args=(patient_id, medical_record_id, ))
    return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=3")


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_create(request, patient_id, record_id, diagnosis_id, template_name="patient/exams.html"):
    form = ComplementaryExamForm(request.POST or None)

    diagnosis = get_object_or_404(Diagnosis, pk=diagnosis_id)
    current_patient = get_object_or_404(Patient, pk=patient_id)

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
                    messages.success(request, 'Exame salvo com sucesso.')

                if request.POST['action'] == "upload":
                    redirect_url = reverse("exam_edit", args=(patient_id, record_id, new_complementary_exam.pk))
                # Nunca entra no save
                elif request.POST['action'] == "save":
                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                else:
                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))

                return HttpResponseRedirect(redirect_url + "?status=edit")
        else:
            messages.error(request, 'Não é possível salvar exame sem arquivos.')

    else:
        file_form = ExamFileForm(request.POST)

    return render(request, template_name,
                  {'viewing': False,
                   'creating': True,
                   'complementary_exam_form': form,
                   'patient_id': patient_id,
                   'record_id': record_id,
                   'name_patient': current_patient.name,
                   'file_form': file_form,
                   'status_mode': 'edit'}, )


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_edit(request, patient_id, record_id, exam_id, template_name="patient/exams.html"):
    current_patient = Patient.objects.get(id=patient_id)
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)

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

                    if request.POST['action'] == "save":
                        messages.success(request, 'Exame salvo com sucesso.')
                        redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                        return HttpResponseRedirect(redirect_url + "?status=edit")
                    else:
                        if request.POST['action'] == 'upload':
                            exam_file_list = ExamFile.objects.filter(exam=exam_id)
                            length = exam_file_list.__len__()
            else:
                messages.error(request, 'Não é possível salvar exame sem arquivos.')

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
                       'name_patient': current_patient.name,
                       'file_form': file_form,
                       'status_mode': 'edit'})


@login_required
@permission_required('patient.view_medicalrecorddata')
def exam_view(request, patient_id, record_id, exam_id, template_name="patient/exams.html"):
    status_mode = request.GET['status']

    current_patient = Patient.objects.get(id=patient_id)
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)
    complementary_exam_form = ComplementaryExamForm(instance=complementary_exam)

    for field in complementary_exam_form.fields:
        complementary_exam_form.fields[field].widget.attrs['disabled'] = True

    try:
        exam_file_list = ExamFile.objects.filter(exam=exam_id)
    except ExamFile.DoesNotExist:
        exam_file_list = None

    return render(request, template_name,
                  {'viewing': True,
                   'creating': False,
                   'complementary_exam_form': complementary_exam_form,
                   'exam_file_list': exam_file_list,
                   'patient_id': patient_id,
                   'record_id': record_id,
                   'name_patient': current_patient.name,
                   'status_mode': status_mode})


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_delete(request, patient_id, record_id, exam_id):
    complementary_exam = get_object_or_404(ComplementaryExam, pk=exam_id)

    if complementary_exam:
        complementary_exam.delete()
        messages.success(request, 'Exame removido com sucesso.')

    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id))
    return HttpResponseRedirect(redirect_url + "?status=edit#tab4")


@login_required
@permission_required('patient.add_medicalrecorddata')
def exam_file_delete(request, exam_file_id):
    exam_file = get_object_or_404(ExamFile, pk=exam_file_id)
    exam_file.delete()
    messages.success(request, 'Anexo removido com sucesso.')

    complementary_exam = get_object_or_404(ComplementaryExam, pk=exam_file.exam_id)
    diagnosis = get_object_or_404(Diagnosis, pk=complementary_exam.diagnosis_id)
    medical_record = get_object_or_404(MedicalRecordData, pk=diagnosis.medical_record_data_id)

    redirect_url = reverse("exam_edit",
                           args=(
                               medical_record.patient_id,
                               diagnosis.medical_record_data_id,
                               complementary_exam.pk))
    return HttpResponseRedirect(redirect_url + "?status=edit")


def get_origin(request):
    origin = '0'

    if 'origin' in request.GET:
        origin = request.GET['origin']
    else:
        if 'origin' in request.POST:
            origin = request.POST['origin']

    return origin


@login_required
# TODO: associate the right permission
# @permission_required('patient.add_medicalrecorddata')
def patient_questionnaire_response_create(request, patient_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):

    patient = get_object_or_404(Patient, pk=patient_id)

    questionnaires_list = Questionnaire.objects.filter(used_also_outside_an_experiment=True)
    unused_questionnaires_list = Questionnaire.objects.filter(used_also_outside_an_experiment=False)

    added_questionnaire = []

    surveys = Questionnaires()

    for questionnaire in questionnaires_list:
        questionnaire.sid = questionnaire.lime_survey_id
        questionnaire.surveyls_title = surveys.get_survey_title(questionnaire.lime_survey_id)

    for questionnaire in unused_questionnaires_list:
        questionnaire.sid = questionnaire.lime_survey_id
        questionnaire.surveyls_title = surveys.get_survey_title(questionnaire.lime_survey_id)

    surveys.release_session_key()

    questionnaire_response_form = None
    fail = None
    redirect_url = None
    questionnaire_response_id = None

    showing = False
    questionnaire = None
    questionnaire_title = None

    if request.method == "GET":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)

    if request.method == "POST":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST)

        if request.POST['action'] == "save":

            questionnaire = get_object_or_404(Questionnaire, lime_survey_id=request.POST['questionnaire_selected'])

            surveys = Questionnaires()
            questionnaire_title = surveys.get_survey_title(questionnaire.lime_survey_id)
            surveys.release_session_key()

            redirect_url, questionnaire_response_id = \
                patient_questionnaire_response_start_fill_questionnaire(request, patient_id, questionnaire)
            if not redirect_url:
                fail = False
            else:
                fail = True
                messages.info(request, 'Você será redirecionado para o questionário. Aguarde.')

                showing = True
                for field in questionnaire_response_form.fields:
                    questionnaire_response_form.fields[field].widget.attrs['disabled'] = True

        if request.POST['action'] == "add_questionnaire":

            questionnaire = \
                get_object_or_404(Questionnaire, lime_survey_id=request.POST['unused_questionnaire_selected'])

            surveys = Questionnaires()

            added_questionnaire = {
                'sid': questionnaire.lime_survey_id,
                'surveyls_title': surveys.get_survey_title(questionnaire.lime_survey_id)
            }
            surveys.release_session_key()

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": None,
        "survey_title": None,
        # "survey_admin": survey_admin,
        "survey_active": None,
        "questionnaire_responsible": request.user.get_username(),
        "creating": True,
        # "subject": get_object_or_404(Subject, pk=subject_id),
        "subject": None,
        "group": None,
        "origin": origin,
        "questionnaires_list": questionnaires_list,
        "unused_questionnaires_list": unused_questionnaires_list,
        "added_questionnaire": added_questionnaire,
        "patient": patient,
        "questionnaire": questionnaire,
        "questionnaire_title": questionnaire_title,
        "showing": showing
    }

    return render(request, template_name, context)


@login_required
# TODO: associate the right permission
# @permission_required('patient.add_medicalrecorddata')
def patient_questionnaire_response_update(request, patient_questionnaire_response_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):

    patient_questionnaire_response = get_object_or_404(PatientQuestionnaireResponse,
                                                       pk=patient_questionnaire_response_id)

    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(patient_questionnaire_response.questionnaire.lime_survey_id)
    survey_active = surveys.get_survey_properties(patient_questionnaire_response.questionnaire.lime_survey_id, 'active')
    survey_completed = (surveys.get_participant_properties(patient_questionnaire_response.questionnaire.lime_survey_id,
                                                           patient_questionnaire_response.token_id,
                                                           "completed") != "N")
    surveys.release_session_key()

    patient = get_object_or_404(Patient, pk=patient_questionnaire_response.patient_id)

    questionnaire_response_form = PatientQuestionnaireResponseForm(None, instance=patient_questionnaire_response)

    fail = None
    redirect_url = None
    questionnaire_response_id = None

    showing = True
    questionnaire = patient_questionnaire_response.questionnaire
    questionnaire_title = survey_title

    if request.method == "POST":
        if request.POST['action'] == "save":
            redirect_url = get_limesurvey_response_url(patient_questionnaire_response)

            if not redirect_url:
                fail = False
            else:
                fail = True
                messages.info(request, 'Você será redirecionado para o questionário. Aguarde.')

        elif request.POST['action'] == "remove":
            surveys = Questionnaires()
            result = surveys.delete_participant(
                patient_questionnaire_response.questionnaire.lime_survey_id,
                patient_questionnaire_response.token_id)
            surveys.release_session_key()

            can_delete = False

            if str(patient_questionnaire_response.token_id) in result:
                result = result[str(patient_questionnaire_response.token_id)]
                if result == 'Deleted' or result == 'Invalid token ID':
                    can_delete = True
            else:
                if 'status' in result and result['status'] == u'Error: Invalid survey ID':
                    can_delete = True

            if can_delete:
                patient_questionnaire_response.delete()
                messages.success(request, 'Preenchimento removido com sucesso')
            else:
                messages.error(request, "Erro ao deletar o preenchimento")

            redirect_url = reverse("patient_edit", args=(patient.id,)) + "?currentTab=4"
            return HttpResponseRedirect(redirect_url)

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": None,
        "patient_questionnaire_response": patient_questionnaire_response,
        "survey_title": survey_title,
        "survey_active": survey_active,
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
        "updating": True
    }

    return render(request, template_name, context)


def patient_questionnaire_response_start_fill_questionnaire(request, patient_id, questionnaire):

    patient_questionnaire_response_form = PatientQuestionnaireResponseForm(request.POST)

    if patient_questionnaire_response_form.is_valid():

        patient_questionnaire_response = patient_questionnaire_response_form.save(commit=False)

        questionnaire_lime_survey = Questionnaires()

        patient = get_object_or_404(Patient, pk=patient_id)

        if not questionnaire_lime_survey.survey_has_token_table(questionnaire.lime_survey_id):
            messages.warning(request,
                             'Preenchimento não disponível - Tabela de tokens não iniciada')
            return None, None

        if questionnaire_lime_survey.get_survey_properties(questionnaire.lime_survey_id, 'active') == 'N':
            messages.warning(request,
                             'Preenchimento não disponível - Questionário não está ativo')
            return None, None

        if not check_required_fields(questionnaire_lime_survey, questionnaire.lime_survey_id):
            messages.warning(request,
                             'Preenchimento não disponível - Questionário não contém campos padronizados')
            return None, None

        result = questionnaire_lime_survey.add_participant(questionnaire.lime_survey_id, patient.name, '',
                                                           patient.email)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(request,
                             'Falha ao gerar token para responder questionário. Verifique se o questionário está ativo')
            return None, None

        patient_questionnaire_response.patient = patient
        patient_questionnaire_response.questionnaire = questionnaire
        patient_questionnaire_response.token_id = result['token_id']
        patient_questionnaire_response.date = datetime.datetime.strptime(request.POST['date'], '%d/%m/%Y')
        patient_questionnaire_response.questionnaire_responsible = request.user
        patient_questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(patient_questionnaire_response)

        return redirect_url, patient_questionnaire_response.pk
    else:
        return None, None


def check_required_fields(surveys, lime_survey_id):
    """
    método para verificar se o questionário tem as questões de identificação corretas
    e se seus tipos também são corretos
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
            question_list = surveys.list_questions(lime_survey_id, group['id'])
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


def get_limesurvey_response_url(patient_questionnaire_response):
    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(
        patient_questionnaire_response.questionnaire.lime_survey_id,
        patient_questionnaire_response.token_id, "token")
    questionnaire_lime_survey.release_session_key()

    redirect_url = \
        '%s/index.php/%s/token/%s/responsibleid/%s/acquisitiondate/%s/subjectid/%s/newtest/Y' % (
            settings.LIMESURVEY['URL_WEB'],
            patient_questionnaire_response.questionnaire.lime_survey_id,
            token,
            str(patient_questionnaire_response.questionnaire_responsible.id),
            patient_questionnaire_response.date.strftime('%d-%m-%Y'),
            str(patient_questionnaire_response.patient.id))

    return redirect_url
