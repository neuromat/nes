# coding=utf-8
import datetime
from functools import partial
import re

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib import messages
from django.db.models import Q

from patient.models import Patient, SocialDemographicData, SocialHistoryData, FleshTone, \
    MaritalStatus, Schooling, Payment, Religion, MedicalRecordData, \
    Gender, AmountCigarettes, AlcoholFrequency, AlcoholPeriod, \
    ClassificationOfDiseases, Diagnosis, ExamFile, ComplementaryExam
from patient.forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm, \
    ComplementaryExamForm, ExamFileForm
from patient.quiz_widget import SelectBoxCountriesDisabled, SelectBoxStateDisabled

from experiment.models import Subject, Experiment, SubjectOfGroup, QuestionnaireConfiguration, QuestionnaireResponse
from experiment.abc_search_engine import Questionnaires


# pylint: disable=E1101
# pylint: disable=E1103

permission_required = partial(permission_required, raise_exception=True)


@login_required
@permission_required('patient.add_patient')
def patient_create(request, template_name="patient/register.html"):
    flesh_tone = FleshTone.objects.all()
    marital_status = MaritalStatus.objects.all()
    gender = Gender.objects.all()
    schooling = Schooling.objects.all()
    payment = Payment.objects.all()
    religion = Religion.objects.all()
    amount_cigarettes = AmountCigarettes.objects.all()
    alcohol_frequency = AlcoholFrequency.objects.all()
    alcohol_period = AlcoholPeriod.objects.all()

    patient_form = PatientForm()
    social_demographic_form = SocialDemographicDataForm()
    social_history_form = SocialHistoryDataForm()

    current_tab = get_current_tab(request)

    if request.method == "POST":

        patient_form = PatientForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)

        if patient_form.is_valid():

            current_tab, new_patient_id = save_patient(current_tab, patient_form, request, social_demographic_form,
                                                       social_history_form, insert_new=True)

            redirect_url = reverse("patient_edit", args=(new_patient_id,))
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))

        else:

            if request.POST['cpf']:
                patient_found = Patient.objects.filter(cpf=request.POST['cpf'])

                if patient_found:

                    if patient_found[0].removed:
                        patient_form.errors['cpf'][0] = "Já existe paciente removido com este CPF."
                    else:
                        patient_form.errors['cpf'][0] = "Já existe paciente cadastrado com este CPF."

    context = {
        'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
        'social_history_form': social_history_form,
        'gender': gender, 'flesh_tone': flesh_tone,
        'marital_status': marital_status, 'schooling': schooling,
        'payment': payment, 'religion': religion,
        'amount_cigarettes': amount_cigarettes, 'alcohol_frequency': alcohol_frequency,
        'alcohol_period': alcohol_period,
        'editing': True,
        'inserting': True,
        'currentTab': current_tab}

    return render(request, template_name, context)


def get_current_tab(request):
    current_tab = '0'

    if request.method == "POST":
        if 'currentTab' in request.POST:
            current_tab = request.POST['currentTab']
    else:
        if 'currentTab' in request.GET:
            current_tab = request.GET['currentTab']

    return current_tab


def save_patient(current_tab, patient_form, request, social_demographic_form, social_history_form, insert_new=False):
    new_patient = patient_form.save(commit=False)
    if not new_patient.cpf:
        new_patient.cpf = None

    if not patient_form.has_changed() \
            and not social_demographic_form.has_changed() \
            and not social_history_form.has_changed():
        return current_tab, new_patient.id

    if patient_form.has_changed():
        new_patient.changed_by = request.user
        new_patient.save()

    if social_demographic_form.is_valid():

        new_social_demographic_data = social_demographic_form.save(commit=False)
        new_social_demographic_data.patient = new_patient

        if insert_new or social_demographic_form.has_changed():

            if (new_social_demographic_data.tv is not None and
                    new_social_demographic_data.radio is not None and
                    new_social_demographic_data.bath is not None and
                    new_social_demographic_data.automobile is not None and
                    new_social_demographic_data.house_maid is not None and
                    new_social_demographic_data.wash_machine is not None and
                    new_social_demographic_data.dvd is not None and
                    new_social_demographic_data.refrigerator is not None and
                    new_social_demographic_data.freezer is not None):

                new_social_demographic_data.social_class = new_social_demographic_data.calculate_social_class(
                    tv=request.POST['tv'], radio=request.POST['radio'],
                    banheiro=request.POST['bath'], automovel=request.POST['automobile'],
                    empregada=request.POST['house_maid'], maquina=request.POST['wash_machine'],
                    dvd=request.POST['dvd'], geladeira=request.POST['refrigerator'],
                    freezer=request.POST['freezer'], escolaridade=request.POST['schooling'])

            else:

                new_social_demographic_data.social_class = None

                if (new_social_demographic_data.tv is not None or
                        new_social_demographic_data.radio is not None or
                        new_social_demographic_data.bath is not None or
                        new_social_demographic_data.automobile is not None or
                        new_social_demographic_data.house_maid is not None or
                        new_social_demographic_data.wash_machine is not None or
                        new_social_demographic_data.dvd is not None or
                        new_social_demographic_data.refrigerator is not None or
                        new_social_demographic_data.freezer is not None):
                    messages.warning(request, 'Classe Social não calculada, pois os campos necessários '
                                              'para o cálculo não foram preenchidos.')
                    current_tab = "1"

            new_social_demographic_data.changed_by = request.user
            new_social_demographic_data.save()

    if insert_new or (social_history_form.is_valid() and social_history_form.has_changed()):
        new_social_history_data = social_history_form.save(commit=False)
        new_social_history_data.patient = new_patient
        new_social_history_data.changed_by = request.user
        new_social_history_data.save()

    if patient_form.has_changed() \
            or social_demographic_form.has_changed() \
            or social_history_form.has_changed():
        messages.success(request, 'Paciente gravado com sucesso.')

    new_patient_id = new_patient.id
    return current_tab, new_patient_id


@login_required
@permission_required('patient.change_patient')
def patient_update(request, patient_id, template_name="patient/register.html"):
    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient and not current_patient.removed:

        patient_form = PatientForm(request.POST or None, instance=current_patient)

        try:
            p_social_demo = SocialDemographicData.objects.get(patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(request.POST or None, instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        try:
            p_social_hist = SocialHistoryData.objects.get(patient_id=patient_id)
            social_history_form = SocialHistoryDataForm(request.POST or None, instance=p_social_hist)
        except SocialHistoryData.DoesNotExist:
            social_history_form = SocialDemographicDataForm()

        current_tab = get_current_tab(request)

        if request.method == "POST":

            if patient_form.is_valid():

                current_tab, new_patient_id = save_patient(current_tab, patient_form, request, social_demographic_form,
                                                           social_history_form)

                redirect_url = reverse("patient_edit", args=(new_patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + current_tab)

            else:
                if request.POST['cpf'] and Patient.objects.filter(cpf=request.POST['cpf']):
                    patient_form.errors['cpf'][0] = "Já existe paciente cadastrado com este CPF."

        medical_data = MedicalRecordData.objects.filter(patient_id=patient_id).order_by('record_date')

        surveys = Questionnaires()
        questionnaires_data = []
        subject = Subject.objects.filter(patient=current_patient)
        subject_of_experiment_list = SubjectOfGroup.objects.filter(subject=subject)
        for subject_of_experiment in subject_of_experiment_list:
            experiment = get_object_or_404(Experiment, id=subject_of_experiment.experiment.id)
            questionnaire_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)
            for questionnaire_configuration in questionnaire_configuration_list:
                questionnaire_response_list = QuestionnaireResponse.objects.filter(subject_of_experiment=subject_of_experiment). \
                    filter(questionnaire_configuration=questionnaire_configuration)
                for questionnaire_response in questionnaire_response_list:
                    questionnaires_data.append(
                        {
                            'experiment_title': experiment.title,
                            'questionnaire_title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
                            'questionnaire_response': questionnaire_response
                        }
                    )


        context = {
            'patient_form': patient_form,
            'social_demographic_form': social_demographic_form,
            'social_history_form': social_history_form,
            'editing': True,
            'currentTab': current_tab,
            'patient_id': patient_id,
            'object_list': medical_data,
            'questionnaire_data': questionnaires_data}
        return render(request, template_name, context)


@login_required
@permission_required('patient.view_patient')
def patient(request, patient_id, template_name="patient/register.html"):
    if request.method == "POST":

        redirect_url = reverse("search_patient")

        if 'action' in request.POST:

            if request.POST['action'] == "remove":

                patient_remove = Patient.objects.get(id=patient_id)
                patient_remove.removed = True
                patient_remove.save()

            else:
                current_tab = request.POST['currentTab']
                redirect_url = reverse("patient_edit", args=(patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))

        return HttpResponseRedirect(redirect_url)

    current_tab = get_current_tab(request)

    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient and not current_patient.removed:

        patient_form = PatientForm(instance=current_patient)

        try:
            p_social_demo = SocialDemographicData.objects.get(patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        try:
            p_social_hist = SocialHistoryData.objects.get(patient_id=patient_id)
            social_history_form = SocialHistoryDataForm(instance=p_social_hist)
        except SocialHistoryData.DoesNotExist:
            social_history_form = SocialDemographicDataForm()

        medical_data = MedicalRecordData.objects.filter(patient_id=patient_id).order_by('record_date')

        for form in {patient_form, social_demographic_form, social_history_form}:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True

        patient_form.fields['country'].widget = SelectBoxCountriesDisabled(
            attrs={'id': 'id_country_state_address', 'data-flags': 'true', 'disabled': 'true'})
        patient_form.fields['state'].widget = SelectBoxStateDisabled(
            attrs={'data-country': 'id_country_state_address', 'id': 'id_chosen_state', 'disabled': 'true'})
        patient_form.fields['citizenship'].widget = SelectBoxCountriesDisabled(
            attrs={'id': 'id_chosen_country', 'data-flags': 'true', 'disabled': 'true'})

        surveys = Questionnaires()
        questionnaires_data = []
        subject = Subject.objects.filter(patient=current_patient)
        subject_of_experiment_list = SubjectOfGroup.objects.filter(subject=subject)
        for subject_of_experiment in subject_of_experiment_list:
            experiment = get_object_or_404(Experiment, id=subject_of_experiment.experiment.id)
            questionnaire_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)
            for questionnaire_configuration in questionnaire_configuration_list:
                questionnaire_response_list = QuestionnaireResponse.objects.filter(subject_of_experiment=subject_of_experiment). \
                    filter(questionnaire_configuration=questionnaire_configuration)
                for questionnaire_response in questionnaire_response_list:
                    questionnaires_data.append(
                        {
                            'experiment_title': experiment.title,
                            'questionnaire_title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
                            'questionnaire_response': questionnaire_response
                        }
                    )

        context = {'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
                   'social_history_form': social_history_form,
                   'editing': False,
                   'currentTab': current_tab,
                   'patient_id': patient_id,
                   'object_list': medical_data,
                   'questionnaire_data': questionnaires_data}

        return render(request, template_name, context)


@login_required
@permission_required('patient.view_patient')
def search_patient(request):
    return render(request, 'patient/busca.html')


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
                patient_list = Patient.objects.filter(name__icontains=search_text).exclude(removed=True)
            else:
                patient_list = Patient.objects.filter(cpf__icontains=search_text).exclude(removed=True)

    return render_to_response('patient/ajax_search.html', {'patients': patient_list})


@login_required
@permission_required('patient.view_patient')
def patients_verify_homonym(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_homonym = Patient.objects.filter(name=search_text).exclude(removed=True)
                patient_homonym_excluded = Patient.objects.filter(name=search_text, removed=True)
            else:
                patient_homonym = Patient.objects.filter(cpf=search_text).exclude(removed=True)
                patient_homonym_excluded = Patient.objects.filter(cpf=search_text, removed=True)
        else:
            patient_homonym = ''
            patient_homonym_excluded = ''

    return render_to_response('patient/ajax_homonym.html', {'patient_homonym': patient_homonym,
                                                         'patient_homonym_excluded': patient_homonym_excluded})


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

        return render_to_response('patient/ajax_cid10.html', {'cid_10_list': cid_10_list, 'medical_record': medical_record,
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
