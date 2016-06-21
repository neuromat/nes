# coding=utf-8
from django.forms import ModelForm, TextInput, PasswordInput, CheckboxSelectMultiple, \
    CharField, ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.forms import PasswordResetForm


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'groups']

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'autofocus': "true",
                                           'placeholder': _('Type first name')}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': _('Type last name')}),
            'username': TextInput(attrs={'class': 'form-control', 'required': "",
                                         'placeholder': _('Type user name')}),
            'password': PasswordInput(attrs={'id': 'id_new_password1', 'required': "",
                                             'class': 'form-control', 'placeholder': _('Type password'),
                                             'onkeyup': "passwordForce(); if(beginCheckPassword1)checkPassExt();"}),
            'email': TextInput(attrs={'class': 'form-control', 'required': "",
                                      'placeholder': _('Type e-mail'), 'id': "email",
                                      'type': 'email', 'data-error': "E-mail inválido",
                                      'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]' +
                                                 '+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
            'groups': CheckboxSelectMultiple(),
        }

    def clean_password(self):
        return make_password(self.cleaned_data['password'])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email, is_active=True).exclude(id=self.instance.id).count():
            raise ValidationError('Este email já existe.')
        return email


class UserFormUpdate(UserForm):
    password = CharField(required=False,
                         widget=PasswordInput(attrs={'id': 'id_new_password1', 'class': 'form-control',
                                                     'placeholder': _('Type password'),
                                                     'onkeyup': "passwordForce(); "
                                                                "if(beginCheckPassword1) checkPassExt();"}))

    def clean_password(self):
        if self.cleaned_data['password']:
            return make_password(self.cleaned_data['password'])
        else:
            return self.instance.password


class CustomPasswordResetForm(PasswordResetForm):

    def is_valid(self):

        if not super(CustomPasswordResetForm, self).is_valid():
            return False

        # get_users returns a generator object
        users = self.get_users(self.cleaned_data["email"])

        try:
            # trying to get the first element from the generator object using __next__() once
            users.__next__()
            return True
        except StopIteration:
            self.add_error('email', _('E-mail is not registered'))
            self.add_error(None, _('E-mail is not registered'))
            return False
