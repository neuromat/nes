__author__ = 'mori'
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import PasswordInput
from django.utils.translation import ugettext_lazy as _

class PasswordChangeFormCustomized(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control',
                                                                  'autofocus': "true", 'required': "",
                                                                  'placeholder': _('Entrar com senha antiga')})
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control', 'required': "",
                                                                   'placeholder': _('Entrar com nova senha'),
                                                                   'onkeyup': "passwordForce();"})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control', 'required': "",
                                                                   'placeholder': _('Entrar novamente com nova senha'),
                                                                   'onkeyup': "checkPass();"})