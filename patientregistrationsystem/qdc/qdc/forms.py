from custom_user.regex_utils import PASSWORD_REGEX, PASSWORD_MIN_LEN
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import PasswordInput, ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordChangeFormCustomized(PasswordChangeForm):
    # MIN_LENGTH = 8
    _password_regex: str = (
        r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    )

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields["old_password"].widget = PasswordInput(
            attrs={
                "class": "form-control",
                "autofocus": "true",
                "required": "",
                "placeholder": _("Current password"),
                "autocomplete": "current-password",
            }
        )

        self.fields["new_password1"].widget = PasswordInput(
            attrs={
                "class": "form-control",
                "required": "",
                "data-minlength": "8",
                "data-maxlength": "128",
                "data-error": "Password must contain at least %d characters, "
                "including at least one uppercase letter, digit or special character."
                % PASSWORD_MIN_LEN,
                "pattern": PASSWORD_REGEX,
                # "pattern": self._password_regex,
                "placeholder": _("New password"),
                "autocomplete": "new-password",
            }
        )

        self.fields["new_password2"].widget = PasswordInput(
            attrs={
                "class": "form-control",
                "required": "",
                "data-match": "#id_new_password1",
                "placeholder": _("Confirm new password"),
                "data-error": _("Passwords don't match"),
                "autocomplete": "new-password",
            }
        )

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")

        # At least MIN_LENGTH long
        if len(password1) < PASSWORD_MIN_LEN:
            raise ValidationError(
                "The new password must be at least %d characters long."
                % PASSWORD_MIN_LEN
            )

        #  at least one uppercase letter, digit or special character
        ok = False
        for character in password1:
            if (
                character.isupper()
                or character.isdigit()
                or character in r"!@#$%&()*+,-./:;<=>?[\]_{|}~'"
            ):
                ok = True
                break
        if not ok:
            raise ValidationError(
                "Password must contain at least %d characters, "
                "including at least one uppercase letter, digit or special character."
                % PASSWORD_MIN_LEN,
            )

        return password1
