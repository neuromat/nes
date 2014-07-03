__author__ = 'mori'
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import CharField, PasswordInput
from django.utils.translation import ugettext_lazy as _


class PasswordChangeFormCustomized(PasswordChangeForm):
    old_password = CharField(label=_("Password"),
                             widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha'}))
    new_password1 = CharField(label=_("Password confirmation"),
                              widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha'}))
    new_password2 = CharField(label=_("Old password"),
                              widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrar senha'}))