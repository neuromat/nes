# coding=utf-8

from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, EmailInput, Select

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

    def __init__(self, *args, **kwargs):
        super(PersonRegisterForm, self).__init__(*args, **kwargs)

        selected_user_list = User.objects.exclude(person=None)

        instance = kwargs.get('instance')
        if instance:
            selected_user_list = selected_user_list.exclude(person=instance)

        self.fields['user'].queryset = User.objects.exclude(pk__in=selected_user_list)
