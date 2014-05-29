# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from models import Patient, SocialDemographicData, SocialHistoryData,FleshToneOption,\
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
    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)
        if patient_form.is_valid():
            new_patient = patient_form.save(commit=False)
            # No futuro não precisará disso:
            new_patient.gender_opt = GenderOption.objects.filter(gender_txt=request.POST['gender_opt'])[0]
            # No futuro não precisará disso:
            new_patient.marital_status_opt = MaritalStatusOption.objects.filter(
                marital_status_txt=request.POST['marital_status_opt'])[0]
            if not new_patient.cpf_id:
                new_patient.cpf_id = None
            new_patient.save()
            if social_demographic_form.is_valid():
                new_social_demographic_data = social_demographic_form.save(commit=False)
                new_social_demographic_data.id_patient = new_patient
                # No futuro não precisará disso:
                new_social_demographic_data.religion_opt = ReligionOption.objects.filter(
                    religion_txt=request.POST['religion_opt'])[0]
                # No futuro não precisará disso:
                new_social_demographic_data.payment_opt = PaymentOption.objects.filter(
                    payment_txt=request.POST['payment_opt'])[0]
                # No futuro não precisará disso:
                new_social_demographic_data.flesh_tone_opt = FleshToneOption.objects.filter(
                    flesh_tone_txt=request.POST['flesh_tone_opt'])[0]
                # No futuro não precisará disso:
                new_social_demographic_data.schooling_opt = SchoolingOption.objects.filter(
                    schooling_txt=request.POST['schooling_opt'])[0]
                #new_social_demographic_data.social_class_opt = new_social_demographic_data.calculateSocialClass(
                #    tv=request.POST['tv_opt'], radio=request.POST['radio_opt'],
                #    banheiro=request.POST['bath_opt'], automovel=request.POST['automobile_opt'],
                #    empregada=request.POST['house_maid_opt'], maquina=request.POST['wash_machine_opt'],
                #    dvd=request.POST['dvd_opt'], geladeira=request.POST['refrigerator_opt'],
                #    freezer=request.POST['freezer_opt'], escolaridade=request.POST['schooling_opt'])

                new_social_demographic_data.save()
            if social_history_form.is_valid():
                new_social_history_data = social_history_form.save(commit=False)
                new_social_history_data.id_patient = new_patient
                if new_social_history_data.smoker == '1':
                    new_social_history_data.amount_cigarettes_opt = AmountCigarettesOption.objects.filter(
                        amount_cigarettes_txt=request.POST['amount_cigarettes_opt'])[0]
                else:
                    new_social_history_data.amount_cigarettes_opt = None
                if new_social_history_data.alcoholic == '1':
                    new_social_history_data.alcohol_frequency_opt = AlcoholFrequencyOption.objects.filter(
                        alcohol_frequency_txt=request.POST['alcohol_frequency_opt'])[0]
                    new_social_history_data.alcohol_period_opt = AlcoholPeriodOption.objects.filter(
                        alcohol_period_txt=request.POST['alcohol_period_opt'])[0]
                else:
                    new_social_history_data.alcohol_frequency_opt = None
                    new_social_history_data.alcohol_period_opt = None
                new_social_history_data.save()
                messages.success(request, 'Paciente gravado com sucesso.')

    context = {'gender_options': gender_options, 'flesh_tone_options': flesh_tone_options,
               'marital_status_options': marital_status_options, 'schooling_options': schooling_options,
               'payment_options': payment_options, 'religion_options': religion_options,
               'amount_cigarettes': amount_cigarettes, 'alcohol_frequency': alcohol_frequency,
               'alcohol_period': alcohol_period, 'patient_form': patient_form}
    return render(request, 'quiz/register.html', context)


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
    flesh_tone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    gender_options = GenderOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    amount_cigarettes = AmountCigarettesOption.objects.all()
    alcohol_frequency = AlcoholFrequencyOption.objects.all()
    alcohol_period = AlcoholPeriodOption.objects.all()

    # Busca na classe models.Patient
    p = Patient.objects.get(nr_record=patient_id)
    patient_form = PatientForm(instance=p)
    if p.dt_birth_txt:
        dt_birth_formatted = str(p.dt_birth_txt.day) + "/"\
                            + str(p.dt_birth_txt.month)\
                            + "/" + str(p.dt_birth_txt.year)
    else:
        dt_birth_formatted = None
    marital_status_searched = p.marital_status_opt_id
    gender_searched = p.gender_opt_id

    # Busca na classe models.SocialDemographicData
    try:
        p_social_demo = SocialDemographicData.objects.get(id_patient_id=patient_id)
    except SocialDemographicData.DoesNotExist:
        p_social_demo = None
    if p_social_demo:
        occupation_searched = p_social_demo.occupation_txt
        profession_searched = p_social_demo.profession_txt
        religion_searched = p_social_demo.religion_opt_id
        benefit_gov_searched = p_social_demo.benefit_gov_bool
        payment_opt_searched = p_social_demo.payment_opt_id
        flesh_tone_opt_searched = p_social_demo.flesh_tone_opt_id
        schooling_opt_searched = p_social_demo.schooling_opt_id
        tv_opt_searched = p_social_demo.tv_opt
        dvd_opt_searched = p_social_demo.dvd_opt
        radio_opt_searched = p_social_demo.radio_opt
        bath_opt_searched = p_social_demo.bath_opt
        automobile_opt_searched = p_social_demo.automobile_opt
        wash_machine_opt_searched = p_social_demo.wash_machine_opt
        refrigerator_opt_searched = p_social_demo.refrigerator_opt
        freezer_opt_searched = p_social_demo.freezer_opt
        house_maid_opt_searched = p_social_demo.house_maid_opt
        social_class_opt_searched = p_social_demo.social_class_opt
    else:
        occupation_searched = None
        profession_searched = None
        religion_searched = None
        benefit_gov_searched = None
        payment_opt_searched = None
        flesh_tone_opt_searched = None
        schooling_opt_searched = None
        tv_opt_searched = None
        dvd_opt_searched = None
        radio_opt_searched = None
        bath_opt_searched = None
        automobile_opt_searched = None
        wash_machine_opt_searched = None
        refrigerator_opt_searched = None
        freezer_opt_searched = None
        house_maid_opt_searched = None
        social_class_opt_searched = None

    # Busca na classe models.SocialDemographicData
    try:
        p_social_hist = SocialHistoryData.objects.get(id_patient_id=patient_id)
    except SocialHistoryData.DoesNotExist:
        p_social_hist = None

    if p_social_hist:
        smoker_searched = p_social_hist.smoker
        amount_cigarettes_opt_searched = p_social_hist.amount_cigarettes_opt_id
        ex_smoker_searched = p_social_hist.ex_smoker
        alcoholic_searched = p_social_hist.alcoholic
        alcohol_frequency_opt_searched = p_social_hist.alcohol_frequency_opt_id
        alcohol_period_opt_searched = p_social_hist.alcohol_period_opt_id
        drugs_opt_searched = p_social_hist.drugs_opt
    else:
        smoker_searched = None
        amount_cigarettes_opt_searched = None
        ex_smoker_searched = None
        alcoholic_searched = None
        alcohol_frequency_opt_searched = None
        alcohol_period_opt_searched = None
        drugs_opt_searched = None

    context = {'patient_form': patient_form, 'citizenship': p.citizenship_txt,
               'country': p.country_txt, 'state': p.state_txt,
               'dt_birth_searched': dt_birth_formatted,
               'flesh_tone_options': flesh_tone_options, 'marital_status_options': marital_status_options,
               'gender_options': gender_options, 'schooling_options': schooling_options,
               'payment_options': payment_options, 'religion_options': religion_options,
               'gender_searched': gender_searched, 'marital_status_searched': marital_status_searched,
               'religion_searched': religion_searched, 'profession_searched': profession_searched,
               'occupation_searched': occupation_searched, 'benefit_gov_searched': benefit_gov_searched,
               'payment_opt_searched': payment_opt_searched, 'flesh_tone_opt_searched': flesh_tone_opt_searched,
               'schooling_opt_searched': schooling_opt_searched, 'tv_opt_searched': tv_opt_searched,
               'dvd_opt_searched': dvd_opt_searched, 'radio_opt_searched': radio_opt_searched,
               'bath_opt_searched': bath_opt_searched, 'automobile_opt_searched': automobile_opt_searched,
               'wash_machine_opt_searched': wash_machine_opt_searched, 'refrigerator_opt_searched': refrigerator_opt_searched,
               'freezer_opt_searched': freezer_opt_searched, 'house_maid_opt_searched': house_maid_opt_searched,
               'social_class_opt_searched': social_class_opt_searched,
               'amount_cigarettes': amount_cigarettes, 'alcohol_frequency': alcohol_frequency,
               'alcohol_period': alcohol_period, 'smoker_searched': smoker_searched,
               'amount_cigarettes_opt_searched': amount_cigarettes_opt_searched, 'ex_smoker_searched': ex_smoker_searched,
               'alcoholic_searched': alcoholic_searched, 'alcohol_frequency_opt_searched': alcohol_frequency_opt_searched,
               'alcohol_period_opt_searched': alcohol_period_opt_searched, 'drugs_opt_searched': drugs_opt_searched,
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
                patients = Patient.objects.filter(name_txt__icontains=search_text)
            else:
                patients = Patient.objects.filter(cpf_id__icontains=search_text)
        else:
            patients = ''
    else:
        search_text = ''

    return render_to_response('quiz/ajax_search.html', {'patients': patients})
