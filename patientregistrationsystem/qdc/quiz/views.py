# coding=utf-8
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.template import RequestContext, loader
from django import forms
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from models import Patient, FleshToneOption, MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption, GenderOption
from forms import PatientForm, SocialDemographicDataForm, SocialHistoryDataForm

from django.contrib import messages

@login_required
def pg_home(request):
    flesh_tone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    gender_options = GenderOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    new_patient = None
    new_personal_data = None
    new_social_demographic_data = None
    new_social_history_data = None
    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)
        if patient_form.is_valid():
            new_patient = patient_form.save(commit=False)
            new_patient.gender_opt = GenderOption.objects.filter(gender_txt=request.POST['gender_opt'])[0]
            new_patient.marital_status_opt = MaritalStatusOption.objects.filter(marital_status_txt=request.POST['marital_status_opt'])[0]
            if not new_patient.cpf_id:
                new_patient.cpf_id = None
            new_patient.save()
            if social_demographic_form.is_valid():
                new_social_demographic_data = social_demographic_form.save(commit=False)
                new_social_demographic_data.id_patient = new_patient
                new_social_demographic_data.religion_opt = ReligionOption.objects.filter(religion_txt=request.POST['religion_opt'])[0]
                new_social_demographic_data.payment_opt = PaymentOption.objects.filter(payment_txt=request.POST['payment_opt'])[0]
                new_social_demographic_data.flesh_tone_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['flesh_tone_opt'])[0]
                new_social_demographic_data.schooling_opt = SchoolingOption.objects.filter(schooling_txt=request.POST['schooling_opt'])[0]
                new_social_demographic_data.save()
                new_social_demographic_data = None
            if social_history_form.is_valid() and False:
                new_social_history_data = social_history_form.save(commit=False)
                new_social_history_data.id_patient = new_patient
                new_social_history_data.save()
                new_social_history_data = None
            messages.add_message(request, messages.INFO, 'Paciente gravado com sucesso.')
        else:

            if not request.POST['name_txt']:
                messages.add_message(request, messages.ERROR, 'Nome não preenchido.')



    context = {'gender_options': gender_options, 'new_social_history_data': new_social_history_data,
               'new_social_demographic_data': new_social_demographic_data,'flesh_tone_options': flesh_tone_options,
               'marital_status_options': marital_status_options, 'schooling_options': schooling_options,
               'payment_options': payment_options, 'religion_options': religion_options, 'new_patient': new_patient,
               'new_personal_data': new_personal_data}
    return render(request, 'quiz/pg_home.html', context)


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

    return render_to_response('pg_home.html', args)


def patient(request, patient_id):
    p = Patient.objects.get(nr_record=patient_id)
    context = {'name': p.name_txt, 'cpf': p.cpf_id, 'rg': p.rg_id, 'place_of_birth': p.natural_of_txt,
               'citizenship': p.citizenship_txt, 'street': p.street_txt, 'zipcode': p.zipcode_number,
               'country': p.country_txt, 'state': p.state_txt, 'city': p.city_txt, 'phone': p.phone_number,
               'cellphone': p.cellphone_number, 'email': p.email_txt, 'medical_record': p.medical_record_number,
               }
    return render(request, 'quiz/pg_home.html', context)


def search_patients(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
        if search_text:
            patients = Patient.objects.filter(name_txt__icontains=search_text)
        else:
            #patients = False
            patients = ''
    else:
        search_text = ''

    #patients = Patient.objects.filter(name_txt__contains=search_text)

    return render_to_response('quiz/ajax_search.html', {'patients': patients})
