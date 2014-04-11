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
    pd = PersonalDataForm
    test = "Test"
    if request.method == "POST":
        test = request.POST
        form = PatientForm(request.POST)
        if form.is_valid():
            new_patient = form.save(commit=False)
    context = {'fleshtone_options': fleshtone_options,'marital_status_options':marital_status_options,'schooling_options':schooling_options,'payment_options':payment_options,'religion_options':religion_options,'test':test,'pd':pd}
    return render(request,'quiz/pg_home.html',context)
