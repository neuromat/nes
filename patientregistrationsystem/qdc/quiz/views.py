# coding=utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from models import Patient, SocialDemographicData, SocialHistoryData, FleshToneOption, \
    MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption, MedicalRecordData, \
    GenderOption, AmountCigarettesOption, AlcoholFrequencyOption, AlcoholPeriodOption, \
    ClassificationOfDiseases, Diagnosis, ExamFile

from forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm, UserForm, UserFormUpdate, \
    MedicalRecordForm, ComplementaryExamForm, ExamFileForm
    MedicalRecordForm, ComplementaryExamForm

from quiz_widget import SelectBoxCountriesDisabled, SelectBoxStateDisabled
from django.contrib import messages

from django.contrib.auth.models import User

# Biblioteca para fazer expressões regulares. Utilizada na "def search_patients_ajax" para fazer busca por nome ou CPF
import re


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

    if 'currentTab' in request.POST:
        current_tab = request.POST['currentTab']
    else:
        current_tab = 0

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


@login_required
@permission_required('quiz.change_patient')
def patient_update(request, patient_id, template_name="quiz/register.html"):
    # # Search in models.Patient
    ## ------------------------
    p = Patient.objects.get(number_record=patient_id)

    if p and not p.removed:

        patient_form = PatientForm(request.POST or None, instance=p)

        ## Search in models.SocialDemographicData
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

        if 'currentTab' in request.GET:
            current_tab = request.GET['currentTab']
        else:
            current_tab = 0

        #TODO: retirar este controle de comentario
        ### teste: inicio

        #TODO: reaproveitar o codigo abaixo, pois eh praticamente igual ao do inserir

        if request.method == "POST":

            if 'currentTab' in request.POST:
                current_tab = request.POST['currentTab']
            else:
                current_tab = 0

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

                    #if homonym_message:
                    #    messages.info(request, homonym_message)

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
def patients(request):
    language = 'en-us'
    session_language = 'en-us'

    if 'lang' in request.COOKIES:
        language = request.COOKIES['lang']

    if 'lang' in request.session:
        session_language = request.session['lang']

    args = {}
    args.update(csrf(request))

    args['patients'] = Patient.objects.all()
    args['language'] = language
    args['session_language'] = session_language

    return render_to_response('/quiz/busca.html', args)


@login_required
@permission_required('quiz.view_patient')
def patient(request, patient_id, template_name="quiz/register.html"):

    if request.method == "POST":

        if 'action' in request.POST:

            if request.POST['action'] == "remove":

                patient_remove = Patient.objects.get(number_record=patient_id)
                patient_remove.removed = True
                patient_remove.save()

                redirect_url = reverse("search_patient")

            else:
                current_tab = request.POST['currentTab']
                redirect_url = reverse("patient_edit", args=(patient_id,))
                return HttpResponseRedirect(redirect_url + "?currentTab=" + str(current_tab))

        return HttpResponseRedirect(redirect_url)

    if 'currentTab' in request.GET:
        current_tab = request.GET['currentTab']
    else:
        current_tab = 0

    # # Search in models.Patient
    ## ------------------------
    p = Patient.objects.get(number_record=patient_id)

    if p and not p.removed:

        patient_form = PatientForm(instance=p)

        ## Search in models.SocialDemographicData
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
                   'object_list': medical_data
        }

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
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = Patient.objects.filter(name_txt__icontains=search_text).exclude(removed=True)
            else:
                patient_list = Patient.objects.filter(cpf_id__icontains=search_text).exclude(removed=True)
        else:
            patient_list = ''
    else:
        search_text = ''

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
    else:
        search_text = ''

    return render_to_response('quiz/ajax_homonym.html', {'patient_homonym': patient_homonym,
                                                         'patient_homonym_excluded': patient_homonym_excluded})

@login_required
def search_cid10_ajax(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
        medical_record = request.POST['medical_record']
        patient_id = request.POST['patient_id']

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(abbreviated_description__icontains=search_text)
        else:
            cid_10_list = ''
    else:
        search_text = ''

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

    p = Patient.objects.get(number_record=patient_id)

    if request.method == "POST":
        if form.is_valid():
            new_medical_record = form.save(commit=False)
            new_medical_record.patient = p
            new_medical_record.record_responsible = request.user
            new_medical_record.save()
            form.save_m2m()
            messages.success(request, 'Avaliação médica salva com sucesso.')
            redirect_url = reverse("patient_edit", args=(p.number_record,))
            return HttpResponseRedirect(redirect_url + "?currentTab=3")

        else:
            messages.error(request, 'Não foi possível criar avaliação médica.')
    return render(request, template_name,
                  {'medical_record_form': form, 'patient_id': patient_id, 'name_patient': p.name_txt,
                   'creating': True, 'editing': True})


def medical_record_view(request, patient_id, record_id, template_name="quiz/medical_record.html"):
    # # Search in models.Patient
    # # ------------------------
    is_editing = (request.GET['status'] == 'edit')

    p = Patient.objects.get(number_record=patient_id)
    m = MedicalRecordData.objects.get(pk=record_id)

    if m:
        medical_record_form = MedicalRecordForm(instance=m)

        diagnosis_list = Diagnosis.objects.filter(medical_record_data=record_id)
        # data = {'object_list': diagnosis_list}

        #deixa os campos como disabled
        for form in {medical_record_form}:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True

        return render(request, template_name,
                      {'medical_record_form': medical_record_form, 'name_patient': p.name_txt, 'patient_id': patient_id,
                       'record_id': m.id, 'object_list': diagnosis_list,
                       'record_date': m.record_date, 'record_responsible': m.record_responsible,
                       'editing': is_editing})


def diagnosis_create(request, patient_id, medical_record_id, cid10_id, template_name="quiz/medical_record.html"):
    # # Search in models.Patient
    # # ------------------------

    # is_editing = (request.GET['status'] == 'edit')

    p = Patient.objects.get(number_record=patient_id)
    m = MedicalRecordData.objects.get(pk=medical_record_id)
    cid10 = ClassificationOfDiseases.objects.get(pk=cid10_id)

    diagnosis = Diagnosis(medical_record_data=m, classification_of_diseases=cid10)
    diagnosis.save()

    redirect_url = reverse("medical_record_view", args=(patient_id, medical_record_id,))
    return HttpResponseRedirect(redirect_url + "?status=edit")

    # diag
    #
    # medical_record_form = MedicalRecordForm(instance=m)
    #
    # return render(request, template_name,
    #               {'medical_record_form': medical_record_form, 'name_patient': p.name_txt, 'patient_id': patient_id,
    #                'diagnosis_list': diagnosis,
    #                'record_date': m.record_date, 'record_responsible': m.record_responsible,
    #                })                  


def exam_create(request, patient_id, record_id, template_name="quiz/exams.html"):

    form = ComplementaryExamForm(request.POST or None)

    d = Diagnosis.objects.get(pk=record_id)
    p = Patient.objects.get(number_record=patient_id)

    if request.method == "POST":
        file_form = ExamFileForm(request.POST, request.FILES)

        if form.is_valid():
            new_complementary_exam = form.save(commit=False)
            new_complementary_exam.diagnosis = d
            new_complementary_exam.save()

            if file_form.is_valid():

                # new_file_data = file_form.save(commit=False)
                # new_file_data.exam = new_complementary_exam
                # new_file_data.save()

                new_document = ExamFile(content=request.FILES['content'])
                new_document.exam = new_complementary_exam
                new_document.save()


            messages.success(request, 'Exame salvo com sucesso.')
            redirect_url = reverse("medical_record_new", args=(p.number_record,))
            return HttpResponseRedirect(redirect_url + "?currentTab=3")

        else:
            messages.error(request, 'Não foi possível criar exame.')
    else:
        file_form = ExamFileForm(request.POST)

    return render(request, template_name,
                  {'complementary_exam_form': form, 'patient_id': patient_id, 'name_patient': p.name_txt,
                   'record_id': record_id, 'file_form': file_form})