# coding=utf-8

from django.forms import ModelForm, TextInput, EmailInput, Select
from django.utils.translation import ugettext_lazy as _

from .models import Person


class PersonRegisterForm(ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'user']

        widgets = {
            'user': Select(attrs={'class': 'form-control', 'autofocus': ''}),
            'first_name': TextInput(attrs={'class': 'form-control', 'required': ""}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': ""}),
            'email': EmailInput(attrs={'class': 'form-control', 'required': ""}),
        }
