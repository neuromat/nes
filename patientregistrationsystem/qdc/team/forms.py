# coding=utf-8

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, EmailInput, Select, PasswordInput, CheckboxSelectMultiple
from django.utils.translation import ugettext as _

from .models import Person, Team, TeamPerson

class PersonRegisterForm(ModelForm):
    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'required': ""}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': ""}),
            'email': EmailInput(attrs={'class': 'form-control', 'required': ""}),
        }


class UserPersonForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'groups']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'required': "", 'disabled': 'disabled',
                                         'placeholder': _('Type a new username')}),
            'password': PasswordInput(attrs={'id': 'id_new_password1', 'required': "",
                                             'class': 'form-control',
                                             'onkeyup': "passwordForce(); if(beginCheckPassword1)checkPassExt();"}),
            'groups': CheckboxSelectMultiple(),
        }

    def clean_password(self):
        return make_password(self.cleaned_data['password'])


class TeamRegisterForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'acronym']

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'required': ""}),
            'acronym': TextInput(attrs={'class': 'form-control'}),
        }


class TeamPersonRegisterForm(ModelForm):
    class Meta:
        model = TeamPerson
        fields = ['person', 'is_coordinator']

        widgets = {
            'person': Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TeamPersonRegisterForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial')
        if initial:
            team = initial['team']
            self.fields['person'].queryset = Person.objects.exclude(team_persons__team=team)
