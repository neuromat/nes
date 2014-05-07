# coding=utf-8
from django.shortcuts import render
from django.http import Http404

from django.http import HttpResponse
from django.template import RequestContext, loader
from django import forms
from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from models import Patient, PersonalData, FleshToneOption, MaritalStatusOption, SchoolingOption, PaymentOption, \
    ReligionOption

from forms import PatientForm, PersonalDataForm


def pg_home(request):
    fleshtone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    #pd = PersonalDataForm
    new_patient = None
    new_personal_data = None
    test = None

    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        test = request.POST
        #personal_data_form = PersonalDataForm(request.POST)
        if patient_form.is_valid():  #and personal_data_form.is_valid():
            new_patient = patient_form.save()
            # new_personal_data = personal_data_form.save()
            # new_personal_data.id_patient = new_patient
            # new_personal_data.city_birth_txt = 'test'
            # new_personal_data.payment_opt = PaymentOption.objects.filter(payment_txt=request.POST['payment_option'])[0]
            # new_personal_data.flesh_tone_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['fleshtone_options'])[0]
            # new_personal_data.gender_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['fleshtone_options'])[0]
    context = {'fleshtone_options': fleshtone_options, 'marital_status_options': marital_status_options,
               'schooling_options': schooling_options, 'payment_options': payment_options,
               'religion_options': religion_options, 'new_patient': new_patient, 'new_personal_data': new_personal_data,
               'test': test}
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
    #personal = PersonalData.objects.get(id_patient=patient_id)
    context = {'name': p.name_txt, 'cpf': p.cpf_id} #debug: incluir "'data_nasc': personal.dt_birth_txt}"
    # Aqui passamos o context para quiz/pg_home.html.
    # Precisamos mostrar os dados de forma que
    # chamemos pg_home(request) para que se dê o
    # processo de atualização do banco de dados
    # caso o usuário submeta novamente o formulário
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
