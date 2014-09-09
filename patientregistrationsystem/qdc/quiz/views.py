# coding=utf-8
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from quiz.models import Patient, SocialDemographicData, SocialHistoryData, FleshToneOption, \
    MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption, MedicalRecordData, \
    GenderOption, AmountCigarettesOption, AlcoholFrequencyOption, AlcoholPeriodOption, \
    ClassificationOfDiseases, Diagnosis, ExamFile, ComplementaryExam

from quiz.forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm, UserForm, UserFormUpdate, \
    ComplementaryExamForm, ExamFileForm

from quiz.quiz_widget import SelectBoxCountriesDisabled, SelectBoxStateDisabled
from django.contrib import messages

from django.contrib.auth.models import User, Group
from django.db.models import Q

from django.core.mail import send_mail
from django.template.context import Context
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.utils.translation import ugettext_lazy as _

import re
from quiz.models import UserProfile

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


def save_patient(current_tab, patient_form, request, social_demographic_form, social_history_form, insert_new=False):
    new_patient = patient_form.save(commit=False)
    if not new_patient.cpf_id:
        new_patient.cpf_id = None

    if not patient_form.has_changed() \
            and not social_demographic_form.has_changed() \
            and not social_history_form.has_changed():
        return current_tab, new_patient.number_record

    if patient_form.has_changed():
        new_patient.changed_by = request.user
        new_patient.save()

    if social_demographic_form.is_valid():

        new_social_demographic_data = social_demographic_form.save(commit=False)
        new_social_demographic_data.id_patient = new_patient

        if insert_new or social_demographic_form.has_changed():

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
                    current_tab = "1"

            new_social_demographic_data.changed_by = request.user
            new_social_demographic_data.save()

    if insert_new or (social_history_form.is_valid() and social_history_form.has_changed()):
        new_social_history_data = social_history_form.save(commit=False)
        new_social_history_data.id_patient = new_patient
        new_social_history_data.changed_by = request.user
        new_social_history_data.save()

    if patient_form.has_changed() \
            or social_demographic_form.has_changed() \
            or social_history_form.has_changed():
        messages.success(request, 'Paciente gravado com sucesso.')

    new_patient_id = new_patient.number_record
    return current_tab, new_patient_id


@login_required
@permission_required('quiz.change_patient')
def patient_update(request, patient_id, template_name="quiz/register.html"):
    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient and not current_patient.removed:

        patient_form = PatientForm(request.POST or None, instance=current_patient)

        try:
            p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(request.POST or None, instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        try:
            p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
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
                if request.POST['cpf_id'] and Patient.objects.filter(cpf_id=request.POST['cpf_id']):
                    patient_form.errors['cpf_id'][0] = "Já existe paciente cadastrado com este CPF."

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

    current_patient = get_object_or_404(Patient, pk=patient_id)

    if current_patient and not current_patient.removed:

        patient_form = PatientForm(instance=current_patient)

        try:
            p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
            social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)
        except SocialDemographicData.DoesNotExist:
            social_demographic_form = SocialDemographicDataForm()

        try:
            p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
            social_history_form = SocialHistoryDataForm(instance=p_social_hist)
        except SocialHistoryData.DoesNotExist:
            social_history_form = SocialDemographicDataForm()

        medical_data = MedicalRecordData.objects.filter(patient_id=patient_id).order_by('record_date')

        for form in {patient_form, social_demographic_form, social_history_form}:
            for field in form.fields:
                form.fields[field].widget.attrs['disabled'] = True

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
@permission_required('auth.add_user', raise_exception=True)
def user_list(request, template_name='quiz/user_list.html'):
    users = User.objects.filter(is_active=True).order_by('username')
    data = {'object_list': users, 'current_user_id': request.user.id}
    return render(request, template_name, data)


@login_required
@permission_required('auth.add_user')
def user_create(request, template_name='quiz/register_users.html'):
    form = UserForm(request.POST or None)
    group_permissions = []
    groups = Group.objects.all()

    for group in groups:
        group_permissions.append(
            {'group': group,
             'checked': False}
        )

    if request.method == "POST":
        if request.POST['action'] == "save":
            if form.is_valid():
                user_added = form.save()
                send_email_user(user_added, request)
                messages.success(request, 'Usuário criado com sucesso.')
                return redirect('user_list')
            else:
                messages.error(request, 'Não foi possível criar usuário.')
    return render(request, template_name, {'form': form, 'group_permissions': group_permissions, 'creating': True})


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
    user_groups = User.objects.get(id=user_id).groups.all()
    group_permissions = []
    groups = Group.objects.all()

    for group in groups:
        if group in user_groups:
            group_permissions.append(
                {'group': group,
                 'checked': True}
            )
        else:
            group_permissions.append(
                {'group': group,
                 'checked': False}
            )

    if request.method == "POST":
        if request.POST['action'] == "save":
            if form.is_valid():
                form.save()

                if request.POST['password']:
                    user = get_object_or_404(User, id=user_id)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.force_password_change = True
                    profile.save()

                messages.success(request, 'Usuário atualizado com sucesso.')
        else:
            if request.POST['action'] == "remove":
                user = get_object_or_404(User, id=user_id)
                user.is_active = False
                user.save()
                messages.success(request, 'Usuário removido com sucesso.')

        return redirect('user_list')

    context = {
        'form': form,
        'editing': True,
        'group_permissions': group_permissions,
        'creating': False
    }
    return render(request, template_name, context)


def send_email_user(user_added=None, request=None, domain_override=None,
                    email_template_name='registration/password_define_email.html',
                    use_https=False, token_generator=default_token_generator):
    """Reset users password"""
    if not user_added.email:
        raise ValueError('Email address is required to send an email')

    if not domain_override:
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
    else:
        site_name = domain = domain_override
    t = loader.get_template(email_template_name)
    c = {
        'email': user_added.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user_added.pk)),  # int_to_base36(user_added.id),
        'user': user_added,
        'token': token_generator.make_token(user_added),
        'protocol': use_https and 'https' or 'http',
    }
    send_mail(_("Definir senha"), t.render(Context(c)), None, [user_added.email])
    # #send_mail(_("Your account for %s") % site_name, t.render(Context(c)), None, [user_added.email])
    # subject_template_name = 'registration/password_reset_subject.txt'
    # subject = loader.render_to_string(subject_template_name, c)
    # # Email subject *must not* contain newlines
    # subject = ''.join(subject.splitlines())
    # # CHANGES START HERE!
    # plain_text_content = loader.render_to_string(email_template_name.replace('with_html', 'plaintext'), c)
    # html_content = loader.render_to_string(email_template_name, c)
    #
    # from django.core.mail import EmailMultiAlternatives
    # msg = EmailMultiAlternatives(subject, plain_text_content, 'jenkins.neuromat@gmail.com', [user_added.email])
    # msg.attach_alternative(html_content, "text/html")
    # msg.send()


@login_required
@permission_required('quiz.add_medicalrecorddata')
def search_cid10_ajax(request):
    cid_10_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']
        medical_record = request.POST['medical_record']
        patient_id = request.POST['patient_id']

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(Q(abbreviated_description__icontains=search_text) |
                                                                  Q(description__icontains=search_text))

        return render_to_response('quiz/ajax_cid10.html', {'cid_10_list': cid_10_list, 'medical_record': medical_record,
                                                           'patient_id': patient_id})


@login_required
@permission_required('quiz.add_medicalrecorddata')
def medical_record_create(request, patient_id, template_name='quiz/medical_record.html'):
    current_patient = get_object_or_404(Patient, pk=patient_id)

    return render(request, template_name,
                  {'name_patient': current_patient.name_txt,
                   'patient_id': patient_id,
                   'creating': True,
                   'editing': True})


@login_required
@permission_required('quiz.view_medicalrecorddata')
def medical_record_view(request, patient_id, record_id, template_name="quiz/medical_record.html"):
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
                      {'name_patient': current_patient.name_txt,
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
@permission_required('quiz.add_medicalrecorddata')
def medical_record_update(request, patient_id, record_id, template_name="quiz/medical_record.html"):
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
                      {'name_patient': current_patient.name_txt,
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
@permission_required('quiz.add_medicalrecorddata')
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
@permission_required('quiz.add_medicalrecorddata')
def medical_record_create_diagnosis_create(request, patient_id, cid10_id):
    current_patient = Patient.objects.get(number_record=patient_id)

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
@permission_required('quiz.add_medicalrecorddata')
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
@permission_required('quiz.add_medicalrecorddata')
def exam_create(request, patient_id, record_id, diagnosis_id, template_name="quiz/exams.html"):
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
                   'name_patient': current_patient.name_txt,
                   'file_form': file_form,
                   'status_mode': 'edit'}, )


@login_required
@permission_required('quiz.add_medicalrecorddata')
def exam_edit(request, patient_id, record_id, exam_id, template_name="quiz/exams.html"):
    current_patient = Patient.objects.get(number_record=patient_id)
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
                       'name_patient': current_patient.name_txt,
                       'file_form': file_form,
                       'status_mode': 'edit'})


@login_required
@permission_required('quiz.view_medicalrecorddata')
def exam_view(request, patient_id, record_id, exam_id, template_name="quiz/exams.html"):
    status_mode = request.GET['status']

    current_patient = Patient.objects.get(number_record=patient_id)
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
                   'name_patient': current_patient.name_txt,
                   'status_mode': status_mode})


@login_required
@permission_required('quiz.add_medicalrecorddata')
def exam_delete(request, patient_id, record_id, exam_id):
    complementary_exam = get_object_or_404(ComplementaryExam, pk=exam_id)

    if complementary_exam:
        complementary_exam.delete()
        messages.success(request, 'Exame removido com sucesso.')

    redirect_url = reverse("medical_record_edit", args=(patient_id, record_id))
    return HttpResponseRedirect(redirect_url + "?status=edit#tab4")


@login_required
@permission_required('quiz.add_medicalrecorddata')
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
