# coding=utf-8
from typing import Any, Iterable

from django.db.models import Model
from custom_user.models import Institution, UserProfile
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    PasswordInput,
    RadioSelect,
    Select,
    TextInput,
    ValidationError,
)
from django.utils.translation import gettext_lazy as _


from custom_user.regex_utils import (
    EMAIL_REGEX,
    FIRSTNAME_REGEX,
    LASTNAME_REGEX,
    PASSWORD_REGEX,
    USERNAME_REGEX,
)


class UserForm(ModelForm):
    first_name = CharField(
        required=True,
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Type first name"),
                "oninput": "this.value = this.value.toUpperCase()",
                "data-maxlength": "150",
            }
        ),
    )
    last_name = CharField(
        required=True,
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Type last name"),
                "oninput": "this.value = this.value.toUpperCase()",
                "data-maxlength": "150",
            }
        ),
    )
    email = CharField(
        required=True,
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Type e-mail"),
                "id": "id_email",
                "type": "email",
                "data-error": _("Invalid e-mail"),
            }
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "email", "groups"]

        widgets = {
            "username": TextInput(
                attrs={
                    "class": "form-control",
                    "name": "username",
                    "required": "",
                    "placeholder": _("Type user name"),
                    "data-minlength": "5",
                    "data-maxlength": "30",
                    "data-error": _(
                        "Username must start with a letter and contain only alphanumeric characters (5-30)"
                    ),
                    "pattern": USERNAME_REGEX,
                }
            ),
            "password": PasswordInput(
                attrs={
                    "id": "id_new_password1",
                    "name": "password",
                    "required": "",
                    "class": "form-control",
                    "placeholder": _("Type password"),
                    "data-minlength": "8",
                    "data-maxlength": "128",
                    "data-error": _(
                        "Password must contain at least a number and a lowercase letter (8-127)"
                    ),
                    "pattern": PASSWORD_REGEX,
                    "onkeyup": "passwordForce(); if(beginCheckPassword1)checkPassExt();",
                }
            ),
            "groups": CheckboxSelectMultiple(),
        }

    def clean_password(self) -> str:
        return make_password(self.cleaned_data["password"])

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email, is_active=True)
            .exclude(id=self.instance.id)
            .count()
        ):
            raise ValidationError(_("E-mail already registered"))
        return email

    def clean_first_name(self) -> str:
        data: str = self.cleaned_data["first_name"]
        return data.upper()

    def clean_last_name(self) -> str:
        data: str = self.cleaned_data["last_name"]
        return data.upper()


class UserFormUpdate(UserForm):
    password = CharField(
        required=False,
        widget=PasswordInput(
            attrs={
                "id": "id_new_password1",
                "class": "form-control",
                "placeholder": _("Type password"),
                "data-minlength": "8",
                "data-maxlength": "128",
                "data-error": _(
                    "Password must contain at least a number and a lowercase letter (8-127)"
                ),
                "pattern": PASSWORD_REGEX,
                "onkeyup": "passwordForce(); if(beginCheckPassword1)checkPassExt();",
            }
        ),
    )

    def clean_password(self):
        if self.cleaned_data["password"]:
            return make_password(self.cleaned_data["password"])
        else:
            return self.instance.password


class CustomPasswordResetForm(PasswordResetForm):
    def is_valid(self) -> bool:
        if not super(CustomPasswordResetForm, self).is_valid():
            return False

        # get_users returns a generator object
        users: Iterable[Any] = self.get_users(self.cleaned_data["email"])

        try:
            # trying to get the first element from the generator object using __next__() once
            iter(users).__next__()
            return True
        except StopIteration:
            self.add_error("email", _("E-mail is not registered"))
            self.add_error(None, _("E-mail is not registered"))
            return False


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["institution", "login_enabled", "citation_name"]

        widgets = {
            "institution": Select(attrs={"class": "form-select"}),
            "login_enabled": RadioSelect(),
            "citation_name": TextInput(
                attrs={"class": "form-control", "placeholder": _("Type citation name")}
            ),
        }


class ResearcherForm(ModelForm):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = CharField(required=True)
    citation_name = CharField(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "citation_name"]

        widgets = {
            "first_name": TextInput(
                attrs={
                    "class": "form-control",
                    "required": "",
                    "placeholder": _("Type first name"),
                    "data-error": _("Only use letters and spaces"),
                    "oninput": "this.value = this.value.toUpperCase()",
                    "data-maxlength": "150",
                }
            ),
            "last_name": TextInput(
                attrs={
                    "class": "form-control",
                    "required": "",
                    "placeholder": _("Type last name"),
                    "data-error": _("Only use letters and spaces"),
                    "oninput": "this.value = this.value.toUpperCase()",
                    "data-maxlength": "1150",
                }
            ),
            "email": TextInput(
                attrs={
                    "name": "email",
                    "class": "form-control",
                    "required": "",
                    "placeholder": _("Type e-mail"),
                    "id": "id_email",
                    "type": "email",
                    "data-error": _("Invalid e-mail"),
                }
            ),
            "citation_name": TextInput(
                attrs={"class": "form-control", "placeholder": _("Type citation name")}
            ),
        }

    def clean_first_name(self) -> str:
        data: str = self.cleaned_data["first_name"]
        return data.upper()

    def clean_last_name(self) -> str:
        data: str = self.cleaned_data["last_name"]
        return data.upper()


class InstitutionForm(ModelForm):
    fields: dict[str, Any]

    class Meta:
        model = Institution
        fields = ["name", "acronym", "country", "parent"]

        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "required": "",
                    "maxlength": "150",
                }
            ),
            "acronym": TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "30",
                }
            ),
            "country": Select(attrs={"class": "form-select"}),
            "parent": Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.fields["country"].initial = "BR"
        instance = kwargs.get("instance") or self.instance

        if instance:
            parent_list = Institution.objects.all()
            parents_to_exclude = get_institutions_recursively(instance)
            for parent in parents_to_exclude:
                parent_list = parent_list.exclude(id=parent.id)
            self.fields["parent"].queryset = parent_list


def get_institutions_recursively(institution: Institution) -> list[Institution]:
    institution_list = [institution]
    children = Institution.objects.filter(parent=institution)
    for child in children:
        if child not in institution_list:
            institution_list.extend(get_institutions_recursively(child))
    return institution_list
