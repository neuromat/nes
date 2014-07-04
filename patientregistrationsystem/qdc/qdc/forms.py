__author__ = 'mori'
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import PasswordInput


class PasswordChangeFormCustomized(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Entrar senha'})
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control',
                                                                   'placeholder': 'Entrar senha',
                                                                   'onkeyup': "password_strong();"})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control',
                                                                   'placeholder': 'Entrar senha',
                                                                   'onkeyup': "checkPass();"})