# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from models import Patient, SocialDemographicData, SocialHistoryData, FleshToneOption,\
    MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption,\
    GenderOption, AmountCigarettesOption, AlcoholFrequencyOption, AlcoholPeriodOption

from forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm
from django.contrib import messages

# Biblioteca para fazer expressões regulares. Utilizada na "def search_patients_ajax" para fazer busca por nome ou CPF
import re


@login_required
def register(request):
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

    if request.method == "POST":

        #obter o nr_record (de algum lugar)
        #patient_id = 95

        #if (patient_id):

            #salvar um paciente jah existente
            #p = Patient.objects.get(nr_record=patient_id)
            #patient_form = PatientForm(request.POST, instance=p)

        #else:

            #salvar um novo paciente
        patient_form = PatientForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)

        if patient_form.is_valid():

            new_patient = patient_form.save(commit=False)

            if not new_patient.cpf_id:
                new_patient.cpf_id = None

            homonym_message = ""
            homonym_list = Patient.objects.filter(name_txt=request.POST['name_txt'])
            if homonym_list:
                homonym_message = "Aviso: existe paciente como o mesmo nome."

            new_patient.save()

            if social_demographic_form.is_valid():

                new_social_demographic_data = social_demographic_form.save(commit=False)
                new_social_demographic_data.id_patient = new_patient

                if(new_social_demographic_data.tv_opt is not None and
                   new_social_demographic_data.radio_opt is not None and
                   new_social_demographic_data.bath_opt is not None and
                   new_social_demographic_data.automobile_opt is not None and
                   new_social_demographic_data.house_maid_opt is not None and
                   new_social_demographic_data.wash_machine_opt is not None and
                   new_social_demographic_data.dvd_opt is not None and
                   new_social_demographic_data.refrigerator_opt is not None and
                   new_social_demographic_data.freezer_opt is not None):

                    new_social_demographic_data.social_class_opt = new_social_demographic_data.calculateSocialClass(
                        tv=request.POST['tv_opt'], radio=request.POST['radio_opt'],
                        banheiro=request.POST['bath_opt'], automovel=request.POST['automobile_opt'],
                        empregada=request.POST['house_maid_opt'], maquina=request.POST['wash_machine_opt'],
                        dvd=request.POST['dvd_opt'], geladeira=request.POST['refrigerator_opt'],
                        freezer=request.POST['freezer_opt'], escolaridade=request.POST['schooling_opt'])
                else:

                    new_social_demographic_data.social_class_opt = None

                    if(new_social_demographic_data.tv_opt is not None or
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

        else:
            if request.POST['cpf_id'] and Patient.objects.filter(cpf_id=request.POST['cpf_id']):
                patient_form.errors['cpf_id'][0] = "Já existe paciente cadastrado com este CPF."

    context = {'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
               'social_history_form': social_history_form,
               'gender_options': gender_options, 'flesh_tone_options': flesh_tone_options,
               'marital_status_options': marital_status_options, 'schooling_options': schooling_options,
               'payment_options': payment_options, 'religion_options': religion_options,
               'amount_cigarettes': amount_cigarettes, 'alcohol_frequency': alcohol_frequency,
               'alcohol_period': alcohol_period}

    return render(request, "quiz/register.html", context)


@login_required
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

    return render_to_response('/quiz/index.html', args)


@login_required
def patient(request, patient_id):

    # Search in models.Patient
    p = Patient.objects.get(nr_record=patient_id)
    patient_form = PatientForm(instance=p)
    if p.dt_birth_txt:
        dt_birth_formatted = "{0}/{1}/{2}".format(str(p.dt_birth_txt.day),
                                                  str(p.dt_birth_txt.month),
                                                  str(p.dt_birth_txt.year))
    else:
        dt_birth_formatted = None

    ## Search in models.SocialDemographicData
    ## --------------------------------------
    try:
        p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
    except SocialDemographicData.DoesNotExist:
        p_social_demo = None

    social_demographic_form = SocialDemographicDataForm(instance=p_social_demo)

    ## Search in models.SocialHistoryData
    ## --------------------------------------
    try:
        p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
    except SocialHistoryData.DoesNotExist:
        p_social_hist = None

    social_history_form = SocialHistoryDataForm(instance=p_social_hist)

    context = {'patient_form': patient_form, 'social_demographic_form': social_demographic_form,
               'social_history_form': social_history_form,
               'dt_birth_txt': dt_birth_formatted,
               }
    return render(request, 'quiz/register.html', context)


@login_required
def search_patient(request):
    return render(request, 'quiz/index.html')


@login_required
def search_patients_ajax(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = Patient.objects.filter(name_txt__icontains=search_text)
            else:
                patient_list = Patient.objects.filter(cpf_id__icontains=search_text)
        else:
            patient_list = ''
    else:
        search_text = ''

    return render_to_response('quiz/ajax_search.html', {'patients': patient_list})
