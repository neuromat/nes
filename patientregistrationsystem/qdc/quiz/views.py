from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django import forms
from django.core.context_processors import csrf


from quiz.models import FleshToneOption, MaritalStatusOption, SchoolingOption, PaymentOption, ReligionOption

from quiz.forms import PatientForm, PersonalDataForm


def pg_home(request):
    fleshtone_options = FleshToneOption.objects.all()
    marital_status_options = MaritalStatusOption.objects.all()
    schooling_options = SchoolingOption.objects.all()
    payment_options = PaymentOption.objects.all()
    religion_options = ReligionOption.objects.all()
    #pd = PersonalDataForm
    new_patient = None
    new_personaldata = None
    test = None
    if request.method == "POST":
        fPacient = PatientForm(request.POST)
        test = request.POST
        fPersonalData = PersonalDataForm(request.POST)
        if fPacient.is_valid() and fPersonalData.is_valid():
            new_patient = fPacient.save(commit=False)
            new_personaldata = fPersonalData.save(commit=False)
            new_personaldata.id_patient = new_patient
            new_personaldata.city_birth_txt = 'test'
    context = {'fleshtone_options': fleshtone_options,'marital_status_options':marital_status_options,'schooling_options':schooling_options,'payment_options':payment_options,'religion_options':religion_options,'new_patient':new_patient,'new_personaldata':new_personaldata,'test':test}
    return render(request,'quiz/pg_home.html',context)
