from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django import forms
from django.core.context_processors import csrf


from models import FleshToneOption, MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption, GenderOption
from forms import PatientForm, PersonalDataForm, SocialDemographicDataForm, SocialHistoryDataForm


def pg_home(request):
    flesh_tone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    gender_options = GenderOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    #pd = PersonalDataForm
    new_patient = None
    new_personal_data = None
    new_social_demographic_data = None
    new_social_history_data = None
    test = None
    if request.method == "POST":
        patient_form = PatientForm(request.POST)
        personal_form = PersonalDataForm(request.POST)
        social_demographic_form = SocialDemographicDataForm(request.POST)
        social_history_form = SocialHistoryDataForm(request.POST)
        test = SocialDemographicDataForm(request.POST)
        if patient_form.is_valid():
            new_patient = patient_form.save()
            if personal_form.is_valid():
                new_personal_data = personal_form.save(commit=False)
                new_personal_data.id_patient = new_patient
                new_personal_data.gender_opt = GenderOption.objects.filter(gender_txt=request.POST['gender_opt'])[0]
                new_personal_data.marital_status_opt = MaritalStatusOption.objects.filter(marital_status_txt=request.POST['marital_status_opt'])[0]
                new_personal_data.save()
                new_personal_data = None
            if social_demographic_form.is_valid():
                new_social_demographic_data = social_demographic_form.save(commit=False)
                new_social_demographic_data.id_patient = new_patient
                new_social_demographic_data.save()
                new_social_demographic_data = None
                new_social_demographic_data.religion_opt = ReligionOption.objects.filter(religion_txt = request.POST['religion_opt'])[0]
                new_personal_data.payment_opt = PaymentOption.objects.filter(payment_txt=request.POST['payment_opt'])[0]
                new_personal_data.flesh_tone_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['flesh_tone_opt'])[0]
            if social_history_form.is_valid():
                new_social_history_data = social_history_form.save(commit=False)
                new_social_history_data.id_patient = new_patient
                #new_social_history_data.amount_cigarettes_opt =
                new_social_history_data.save()
                new_social_history_data = None
    context = {'gender_options': gender_options, 'new_social_history_data': new_social_history_data, 'new_social_demographic_data':new_social_demographic_data,'flesh_tone_options': flesh_tone_options,'marital_status_options':marital_status_options,'schooling_options':schooling_options,'payment_options':payment_options,'religion_options':religion_options,'new_patient':new_patient,'new_personal_data':new_personal_data,'test':test}
    return render(request, 'quiz/pg_home.html', context)
