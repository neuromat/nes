# coding=utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from models import Patient, SocialDemographicData, SocialHistoryData, FleshToneOption, \
    MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption, MedicalRecordData, \
    GenderOption, AmountCigarettesOption, AlcoholFrequencyOption, AlcoholPeriodOption, \
    ClassificationOfDiseases, Diagnosis, ExamFile, ComplementaryExam

from forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm, UserForm, UserFormUpdate, \
    MedicalRecordForm, ComplementaryExamForm, ExamFileForm

from quiz_widget import SelectBoxCountriesDisabled, SelectBoxStateDisabled
from django.contrib import messages

from django.contrib.auth.models import User

# Biblioteca para fazer expressões regulares. Utilizada na "def search_patients_ajax" para fazer busca por nome ou CPF
import re

# pylint: disable=E1101
# pylint: disable=E1103


@login_required
@permission_required('quiz.add_patient')
def patient_create(request, template_name="quiz/register.html"):
    flesh_tone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    gender_options = GenderOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    amount_cigarettes = AmountCigarettesOption.objects.all()
    alcohol_frequency = AlcoholFrequencyOption.objects.all()
    alcohol_period = AlcoholPeriodOption.objects.all()

    # formularios a salvar
    patient_form = PatientForm()
    social_demographic_form = SocialDemographicDataForm()
    social_history_form = SocialHistoryDataForm()

    current_tab = get_current_tab(request)

    if request.method == "POST":

        patient_form = PatientForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)

        if patient_form.is_valid():

            new_patient = patient_form.save(commit=False)

            if not new_patient.cpf_id:
                new_patient.cpf_id = None

            homonym_message = ""
            homonym_list = Patient.objects.filter(name_txt=request.POST['name_txt']).exclude(removed=True)
            if homonym_list:
                homonym_message = "Aviso: existe paciente com o mesmo nome."

            new_patient.save()

            if social_demographic_form.is_valid():

                new_social_demographic_data = social_demographic_form.save(commit=False)
                new_social_demographic_data.id_patient = new_patient

                if (new_social_demographic_data.tv_opt is not None and
                        new_social_demographic_data.radio_opt is not None and
                        new_social_demographic_data.bath_opt is not None and
                        new_social_demographic_data.automobile_opt is not None and
                        new_social_demographic_data.house_maid_opt is not None and
                        new_social_demographic_data.wash_machine_opt is not None and
                        new_social_demographic_data.dvd_opt is not None and
                        new_social_demographic_data.refrigerator_opt is not None and
                        new_social_demographic_data.freezer_opt is not None):

                    new_social_demographic_data.social_class_opt = new_social_demographic_data.calculate_social_class(
                        tv=request.POST['tv_opt'], radio=request.POST['radio_opt'],
                        banheiro=request.POST['bath_opt'], automovel=request.POST['automobile_opt'],
                        empregada=request.POST['house_maid_opt'], maquina=request.POST['wash_machine_opt'],
                        dvd=request.POST['dvd_opt'], geladeira=request.POST['refrigerator_opt'],
                        freezer=request.POST['freezer_opt'], escolaridade=request.POST['schooling_opt'])
                else:

                    new_social_demographic_data.social_class_opt = None

                    if (new_social_demographic_data.tv_opt is not None or
                            new_social_demographic_data.radio_opt is not None or
                            new_social_demographic_data.bath_opt is not None or
                            new_social_demographic_data.automobile_opt is not None or
                            new_social_demographic_data.house_maid_opt is not None or
                            new_social_demographic_data.wash_machine_opt is not None or
                            new_social_demographic_data.dvd_opt is not None or
                            new_social_demographic_data.refrigerator_opt is not None or
                            new_social_demographic_data.freezer_opt is not None):
                        messages.warning(request, 'Classe Social não calculada, pois os campos necessários '
                                                  'para o cálculo não foram preenchidos.')

                new_social_demographic_data.save()

            if social_history_form.is_valid():
                new_social_history_data = social_history_form.save(commit=False)
                new_social_history_data.id_patient = new_patient
                new_social_history_data.save()

                messages.success(request, 'Paciente gravado com sucesso.')

                if homonym_message:
                    messages.info(request, homonym_message)

            new_patient_id = new_patient.number_record

            redirect_url = reverse("patient_edit", args=(new_patient_id,))
            return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))

        else:

            if request.POST['cpf_id']:
                patient_found = Patient.objects.filter(cpf_id=request.POST['cpf_id'])

                if patient_found:

                    if patient_found[0].removed:
                        patient_form.errors['cpf_id'][0] = "Já existe paciente removido com este CPF."
                    else:
                        patient_form.errors['cpf_id'][0] = "Já existe paciente cadastrado com este CPF."

    context = {
        'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
        'social_history_form': social_history_form,
        'gender_options': gender_options, 'flesh_tone_options': flesh_tone_options,
        'marital_status_options': marital_status_options, 'schooling_options': schooling_options,
        'payment_options': payment_options, 'religion_options': religion_options,
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


@login_required
@permission_required('quiz.change_patient')
def patient_update(request, patient_id, template_name="quiz/register.html"):

    # # Search in models.Patient
    # # ------------------------    
    p = get_object_or_404(Patient, pk=patient_id)

    if p and not p.removed:

        patient_form = PatientForm(request.POST or None, instance=p)

        # # Search in models.SocialDemographicData
        ## --------------------------------------
        try:
            p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(request.POST or None, instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        ## Search in models.SocialHistoryData
        ## --------------------------------------
        try:
            p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
            social_history_form = SocialHistoryDataForm(request.POST or None, instance=p_social_hist)
        except SocialHistoryData.DoesNotExist:
            social_history_form = SocialDemographicDataForm()

        current_tab = get_current_tab(request)
        #TODO: retirar este controle de comentario
        ### teste: inicio

        #TODO: reaproveitar o codigo abaixo, pois eh praticamente igual ao do inserir

        if request.method == "POST":

            #patient_form = PatientForm(request.POST)
            #social_demographic_form = SocialDemographicDataForm(request.POST)
            #social_history_form = SocialHistoryDataForm(request.POST)

            if patient_form.is_valid():

                new_patient = patient_form.save(commit=False)

                if not new_patient.cpf_id:
                    new_patient.cpf_id = None

                #homonym_message = ""
                #homonym_list = Patient.objects.filter(name_txt=request.POST['name_txt'])
                #if homonym_list:
                #    homonym_message = "Aviso: existe paciente como o mesmo nome."

                new_patient.save()

                if social_demographic_form.is_valid():

                    new_social_demographic_data = social_demographic_form.save(commit=False)
                    new_social_demographic_data.id_patient = new_patient

                    if (new_social_demographic_data.tv_opt is not None and
                            new_social_demographic_data.radio_opt is not None and
                            new_social_demographic_data.bath_opt is not None and
                            new_social_demographic_data.automobile_opt is not None and
                            new_social_demographic_data.house_maid_opt is not None and
                            new_social_demographic_data.wash_machine_opt is not None and
                            new_social_demographic_data.dvd_opt is not None and
                            new_social_demographic_data.refrigerator_opt is not None and
                            new_social_demographic_data.freezer_opt is not None):

                        new_social_demographic_data.social_class_opt = \
                            new_social_demographic_data.calculate_social_class(
                                tv=request.POST['tv_opt'], radio=request.POST['radio_opt'],
                                banheiro=request.POST['bath_opt'], automovel=request.POST['automobile_opt'],
                                empregada=request.POST['house_maid_opt'], maquina=request.POST['wash_machine_opt'],
                                dvd=request.POST['dvd_opt'], geladeira=request.POST['refrigerator_opt'],
                                freezer=request.POST['freezer_opt'], escolaridade=request.POST['schooling_opt'])
                    else:

                        new_social_demographic_data.social_class_opt = None

                        if (new_social_demographic_data.tv_opt is not None or
                                new_social_demographic_data.radio_opt is not None or
                                new_social_demographic_data.bath_opt is not None or
                                new_social_demographic_data.automobile_opt is not None or
                                new_social_demographic_data.house_maid_opt is not None or
                                new_social_demographic_data.wash_machine_opt is not None or
                                new_social_demographic_data.dvd_opt is not None or
                                new_social_demographic_data.refrigerator_opt is not None or
                                new_social_demographic_data.freezer_opt is not None):
                            messages.warning(request, 'Classe Social não calculada, pois os campos necessários '
                                                      'para o cálculo não foram preenchidos.')
                            current_tab = "1"

                    new_social_demographic_data.save()

                if social_history_form.is_valid():
                    new_social_history_data = social_history_form.save(commit=False)
                    new_social_history_data.id_patient = new_patient

                    new_social_history_data.save()

                    messages.success(request, 'Paciente gravado com sucesso.')

                new_patient_id = new_patient.number_record

                redirect_url = reverse("patient_edit", args=(new_patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + current_tab)

            else:
                if request.POST['cpf_id'] and Patient.objects.filter(cpf_id=request.POST['cpf_id']):
                    patient_form.errors['cpf_id'][0] = "Já existe paciente cadastrado com este CPF."

        #TODO: retirar este controle de comentario
        ### teste: fim

        medical_data = MedicalRecordData.objects.filter(patient_id=patient_id).order_by('record_date')

        context = {
            'patient_form': patient_form,
            'social_demographic_form': social_demographic_form,
            'social_history_form': social_history_form,
            'editing': True,
            'currentTab': current_tab,
            'patient_id': patient_id,
            'object_list': medical_data}
        return render(request, template_name, context)


@login_required
@permission_required('quiz.view_patient')
def patient(request, patient_id, template_name="quiz/register.html"):

    if request.method == "POST":

        redirect_url = reverse("search_patient")

        if 'action' in request.POST:

            if request.POST['action'] == "remove":

                patient_remove = Patient.objects.get(number_record=patient_id)
                patient_remove.removed = True
                patient_remove.save()

            else:
                current_tab = request.POST['currentTab']
                redirect_url = reverse("patient_edit", args=(patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))

        return HttpResponseRedirect(redirect_url)

    current_tab = get_current_tab(request)

    p = get_object_or_404(Patient, pk=patient_id)

    if p and not p.removed:

        patient_form = PatientForm(instance=p)

        # # Search in models.SocialDemographicData
        ## --------------------------------------
        try:
            p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        ## Search in models.SocialHistoryData
        ## ----------------------------------
        try:
            p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
            social_history_form = SocialHistoryDataForm(instance=p_social_hist)
        except SocialHistoryData.DoesNotExist:
            social_history_form = SocialDemographicDataForm()

        medical_data = MedicalRecordData.objects.filter(patient_id=patient_id).order_by('record_date')

        #deixa os campos como disabled
        for form in {patient_form, social_demographic_form, social_history_form}:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True

        #Sobrescreve campos Pais, Nacionalidade e Estado
        patient_form.fields['country_txt'].widget = SelectBoxCountriesDisabled(
            attrs={'id': 'id_country_state_address', 'data-flags': 'true', 'disabled': 'true'})
        patient_form.fields['state_txt'].widget = SelectBoxStateDisabled(
            attrs={'data-country': 'id_country_state_address', 'id': 'id_chosen_state', 'disabled': 'true'})
        patient_form.fields['citizenship_txt'].widget = SelectBoxCountriesDisabled(
            attrs={'id': 'id_chosen_country', 'data-flags': 'true', 'disabled': 'true'})

        context = {'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
                   'social_history_form': social_history_form,
                   'editing': False,
                   'currentTab': current_tab,
                   'patient_id': patient_id,
                   'object_list': medical_data}

        return render(request, template_name, context)


@login_required
@permission_required('quiz.view_patient')
def search_patient(request):
    return render(request, 'quiz/busca.html')


@login_required
def advanced_search(request):
    return render(request, 'quiz/busca_avancada.html')


@login_required
def contact(request):
    return render(request, 'quiz/contato.html')


@login_required
def restore_patient(request, patient_id):
    patient_restored = Patient.objects.get(number_record=patient_id)
    patient_restored.removed = False
    patient_restored.save()

    redirect_url = reverse("patient_view", args=(patient_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('quiz.view_patient')
def search_patients_ajax(request):
    patient_list = ''
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = Patient.objects.filter(name_txt__icontains=search_text).exclude(removed=True)
            else:
                patient_list = Patient.objects.filter(cpf_id__icontains=search_text).exclude(removed=True)

    return render_to_response('quiz/ajax_search.html', {'patients': patient_list})


@login_required
@permission_required('quiz.view_patient')
def patients_verify_homonym(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_homonym = Patient.objects.filter(name_txt=search_text).exclude(removed=True)
                patient_homonym_excluded = Patient.objects.filter(name_txt=search_text, removed=True)
            else:
                patient_homonym = Patient.objects.filter(cpf_id=search_text).exclude(removed=True)
                patient_homonym_excluded = Patient.objects.filter(cpf_id=search_text, removed=True)
        else:
            patient_homonym = ''
            patient_homonym_excluded = ''

    return render_to_response('quiz/ajax_homonym.html', {'patient_homonym': patient_homonym,
                                                         'patient_homonym_excluded': patient_homonym_excluded})


@login_required
def search_cid10_ajax(request):

    cid_10_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']
        medical_record = request.POST['medical_record']
        patient_id = request.POST['patient_id']

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(abbreviated_description__icontains=search_text)

    return render_to_response('quiz/ajax_cid10.html', {'cid_10_list': cid_10_list, 'medical_record': medical_record,
                                                       'patient_id': patient_id})


@login_required
@permission_required('auth.add_user')
@permission_required('auth.change_user')
def user_list(request, template_name='quiz/user_list.html'):
    users = User.objects.filter(is_active=True).order_by('username')
    data = {'object_list': users, 'current_user_id': request.user.id}
    return render(request, template_name, data)


@login_required
@permission_required('auth.add_user')
def user_create(request, template_name='quiz/register_users.html'):
    form = UserForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('user_list')
        else:
            messages.error(request, 'Não foi possível criar usuário.')
    return render(request, template_name, {'form': form})


@login_required
@permission_required('auth.delete_user')
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, 'Usuário removido com sucesso.')
    return redirect('user_list')


@login_required
@permission_required('auth.change_user')
def user_update(request, user_id, template_name="quiz/register_users.html"):
    form = UserFormUpdate(request.POST or None, instance=User.objects.get(id=user_id))
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso.')
            return redirect('user_list')

    context = {
        'form': form,
        'editing': True,
    }
    return render(request, template_name, context)


@login_required
# @permission_required('auth.add_user')
def medical_record_create(request, patient_id, template_name='quiz/medical_record.html'):
    form = MedicalRecordForm(request.POST or None)

    patient_new = Patient.objects.get(number_record=patient_id)

    if request.method == "POST":

        if form.is_valid():

            # verificar se algo foi preenchido
            new_medical_record = form.save(commit=False)
            new_medical_record.patient = patient_new
            new_medical_record.record_responsible = request.user
            new_medical_record.save()
            form.save_m2m()

            messages.success(request, 'Avaliação médica salva com sucesso.')

            # redirect_url = reverse("patient_edit", args=(patient_new.number_record,))
            # return HttpResponseRedirect(redirect_url + "?currentTab=3")

            redirect_url = reverse("medical_record_edit", args=(patient_id, new_medical_record.id))
            return HttpResponseRedirect(redirect_url + "?status=edit")

        else:
            messages.error(request, 'Não foi possível criar avaliação médica.')

    return render(request, template_name,
                  {'medical_record_form': form, 'patient_id': patient_id, 'name_patient': patient_new.name_txt,
                   'creating': True, 'editing': True})


def medical_record_view(request, patient_id, record_id, template_name="quiz/medical_record.html"):

    status_mode = request.GET['status']

    current_patient = Patient.objects.get(number_record=patient_id)
    medical_record = MedicalRecordData.objects.get(pk=record_id)

    if medical_record:
        medical_record_form = MedicalRecordForm(instance=medical_record)

        diagnosis_list = Diagnosis.objects.filter(medical_record_data=record_id)
        complementary_exams_list = []
        for diagnosis in diagnosis_list:
            complementary_exams_list.append(ComplementaryExam.objects.filter(diagnosis=diagnosis.pk))

        lists_diagnosis_exams = zip(diagnosis_list, complementary_exams_list)

        # deixa os campos como disabled
        for form in {medical_record_form}:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True

        return render(request, template_name,
                      {'medical_record_form': medical_record_form,
                       'name_patient': current_patient.name_txt,
                       'patient_id': patient_id,
                       'record_id': medical_record.id,
                       'object_list': diagnosis_list,
                       'lists_diagnosis_exams': lists_diagnosis_exams,
                       'complementary_exams_list': complementary_exams_list,
                       'record_date': medical_record.record_date,
                       'record_responsible': medical_record.record_responsible,
                       'editing': False,
                       'status_mode': status_mode})


def medical_record_update(request, patient_id, record_id, template_name="quiz/medical_record.html"):

    status_mode = request.GET['status']
    current_tab = get_current_tab(request)

    current_patient = Patient.objects.get(number_record=patient_id)
    medical_record = MedicalRecordData.objects.get(pk=record_id)

    if medical_record:

        medical_record_form = MedicalRecordForm(request.POST or None, instance=medical_record)
        diagnosis_list = Diagnosis.objects.filter(medical_record_data=record_id)
        complementary_exams_list = []

        for diagnosis in diagnosis_list:
            complementary_exams_list.append(ComplementaryExam.objects.filter(diagnosis=diagnosis.pk))

        lists_diagnosis_exams = zip(diagnosis_list, complementary_exams_list)

        if request.method == "POST":

            if medical_record_form.is_valid():

                medical_record_form.save()
                messages.success(request, 'Avaliação médica salva com sucesso.')

                redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=" + current_tab)

        return render(request, template_name,
                      {'medical_record_form': medical_record_form,
                       'name_patient': current_patient.name_txt,
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


def diagnosis_create(request, patient_id, medical_record_id, cid10_id):

    m = MedicalRecordData.objects.get(pk=medical_record_id)
    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    diagnosis = Diagnosis(medical_record_data=m, classification_of_diseases=cid10)
    diagnosis.save()

    redirect_url = reverse("medical_record_edit", args=(patient_id, medical_record_id,))
    return HttpResponseRedirect(redirect_url + "?status=edit&currentTab=3")


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


def exam_create(request, patient_id, record_id, diagnosis_id, template_name="quiz/exams.html"):
    form = ComplementaryExamForm(request.POST or None)

    d = Diagnosis.objects.get(pk=diagnosis_id)
    p = Patient.objects.get(number_record=patient_id)

    if request.method == "POST":
        file_form = ExamFileForm(request.POST, request.FILES)

        if form.is_valid():
            new_complementary_exam = form.save(commit=False)
            new_complementary_exam.diagnosis = d
            new_complementary_exam.save()

            if file_form.is_valid():
                new_file_data = file_form.save(commit=False)
                new_file_data.exam = new_complementary_exam
                new_file_data.save()

            messages.success(request, 'Exame salvo com sucesso.')

            if request.POST['action'] == "upload":
                redirect_url = reverse("exam_edit", args=(patient_id, record_id, diagnosis_id,
                                                          new_complementary_exam.pk))
            elif request.POST['action'] == "save":
                redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
            else:
                redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
            return HttpResponseRedirect(redirect_url + "?status=edit")

        else:
            messages.error(request, 'Não foi possível criar exame.')
    else:
        file_form = ExamFileForm(request.POST)

    return render(request, template_name,
                  {'complementary_exam_form': form, 'patient_id': patient_id,
                   'name_patient': p.name_txt, 'record_id': record_id,
                   'file_form': file_form, 'viewing': False},)


def exam_edit(request, patient_id, record_id, diagnosis_id, exam_id, template_name="quiz/exams.html"):

    p = Patient.objects.get(number_record=patient_id)
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)

    if complementary_exam:
        complementary_exam_form = ComplementaryExamForm(request.POST or None, instance=complementary_exam)
        exam_file_list = ExamFile.objects.filter(exam=exam_id)

        if request.method == "POST":
            file_form = ExamFileForm(request.POST, request.FILES)

            if complementary_exam_form.is_valid():
                complementary_exam_form.save()

                if file_form.is_valid():
                    new_file_data = file_form.save(commit=False)
                    new_file_data.exam = complementary_exam
                    new_file_data.save()

                messages.success(request, 'Exame salvo com sucesso.')

                if request.POST['action'] == "save":
                    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id, ))
                    return HttpResponseRedirect(redirect_url + "?status=edit")

            else:
                messages.error(request, 'Não foi possível salvar exame.')

        else:
            file_form = ExamFileForm(request.POST)

        return render(request, template_name,
                      {'viewing': True, 'complementary_exam_form': complementary_exam_form,
                       'exam_file_list': exam_file_list, 'patient_id': patient_id,
                       'record_id': record_id, 'name_patient': p.name_txt, 'file_form': file_form})


def exam_view(request, patient_id, record_id, diagnosis_id, exam_id, template_name="quiz/exams.html"):

    p = Patient.objects.get(number_record=patient_id)
    #is_editing = (request.GET['status'] == 'edit')
    complementary_exam = ComplementaryExam.objects.get(pk=exam_id)
    complementary_exam_form = ComplementaryExamForm(instance=complementary_exam)

    for field in complementary_exam_form.fields:
        complementary_exam_form.fields[field].widget.attrs['disabled'] = True

    try:
        exam_file_list = ExamFile.objects.filter(exam=exam_id)
    except ExamFile.DoesNotExist:
        exam_file_list = None

    return render(request, template_name,
                  {'complementary_exam_form': complementary_exam_form,
                   'exam_file_list': exam_file_list, 'viewing': True, 'patient_id': patient_id,
                   'record_id': record_id, 'name_patient': p.name_txt})
