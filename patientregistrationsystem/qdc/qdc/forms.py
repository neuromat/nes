from django.contrib.auth.forms import PasswordChangeForm
from django.forms import PasswordInput, ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordChangeFormCustomized(PasswordChangeForm):

    MIN_LENGTH = 8

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['old_password'].widget = PasswordInput(
            attrs={'class': 'form-control', 'autofocus': "true", 'required': "",
                   'placeholder': _('Current password')})

        self.fields['new_password1'].widget = PasswordInput(
            attrs={'class': 'form-control', 'required': "",
                   'data-minlength': '8',
                   'data-error': "Password must contain at least 8 characters, "
                                 "including at least one uppercase letter, digit or special character.",
                   'pattern': "([a-z]*([A-Z]|[0-9]|[ !@#\$%&'\(\)\*\+,-\.\/:;<=>\?\[\\\\\]_\{\|\}~])[a-z]*){1,}",
                   'placeholder': _('New password')})

        self.fields['new_password2'].widget = PasswordInput(
            attrs={'class': 'form-control', 'required': "",
                   'data-match': '#id_new_password1',
                   'placeholder': _('Confirm new password')})

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        # At least MIN_LENGTH long
        if len(password1) < self.MIN_LENGTH:
            raise ValidationError("The new password must be at least %d characters long." % self.MIN_LENGTH)

        #  at least one uppercase letter, digit or special character
        ok = False
        for character in password1:
            if character.isupper() or character.isdigit() or character in ' !@#$%&''"()*+,-./:;<=>?[\]_{|}~':
                ok = True
                break
        if not ok:
            raise ValidationError("Password must contain at least 8 characters, "
                                  "including at least one uppercase letter, digit or special character.")

        return password1
