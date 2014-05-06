from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django import forms
from django.core.context_processors import csrf


from quiz.models import FleshToneOption, MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption

from quiz.forms import PatientForm, PersonalDataForm

@login_required
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
        if patient_form.is_valid(): #and personal_data_form.is_valid():
            new_patient = patient_form.save()
            #new_personal_data = personal_data_form.save(commit=False)
            #new_personal_data.id_patient = new_patient
            #new_personal_data.city_birth_txt = 'test'
            #new_personal_data.payment_opt = PaymentOption.objects.filter(payment_txt=request.POST['payment_option'])[0]
            #new_personal_data.flesh_tone_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['fleshtone_options'])[0]
            #new_personal_data.gender_opt = FleshToneOption.objects.filter(flesh_tone_txt=request.POST['fleshtone_options'])[0]
    context = {'fleshtone_options': fleshtone_options,'marital_status_options':marital_status_options,'schooling_options':schooling_options,'payment_options':payment_options,'religion_options':religion_options,'new_patient':new_patient,'new_personal_data':new_personal_data,'test':test}
    return render(request,'quiz/pg_home.html',context)
