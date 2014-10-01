# coding=utf-8
from django.forms import ModelForm, TextInput, PasswordInput, CheckboxSelectMultiple, \
    CharField, ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'groups']

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar primeiro nome'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar último nome'}),
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar nome de usuário'}),
            'password': PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha',
                                             'onkeyup': "password_strong(); if(beginCheckPassword1)checkPass();"}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrar e-mail', 'id': "email",
                                      'type': 'email', 'data-error': "E-mail inválido",
                                      'pattern': '^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]' +
                                                 '+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$'}),
            'groups': CheckboxSelectMultiple(),
        }

    def clean_password(self):
        return make_password(self.cleaned_data['password'])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email, is_active=True).exclude(username=username).count():
            raise ValidationError(u'Este email já existe.')
        return email


class UserFormUpdate(UserForm):
    password = CharField(required=False,
                         widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha',
                                                     'onkeyup': "password_strong();"
                                                                "if(beginCheckPassword1)checkPass();"}))

    def clean_password(self):
        if self.cleaned_data['password']:
            return make_password(self.cleaned_data['password'])
        else:
            return self.instance.password
