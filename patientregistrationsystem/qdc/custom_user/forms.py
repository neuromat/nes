# coding=utf-8
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


class UserForm(ModelForm):
    first_name = CharField(
        required=True,
        widget=TextInput(
            attrs={
                "class": "form-control",
                "autofocus": "true",
                "placeholder": _("Type first name"),
                "pattern": "^[A-z]{1,}([- ]{0,1}[A-z]{0,}){0,3}[A-z]$",
            }
        ),
    )
    last_name = CharField(
        required=True,
        widget=TextInput(
            attrs={
                "class": "form-control",
                "autofocus": "true",
                "placeholder": _("Type last name"),
                "pattern": "^[A-z]{1,}([- ]{0,1}[A-z]{0,}){0,3}[A-z]$",
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
                "data-error": "E-mail inválido",
                "pattern": "^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$",
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
                    "required": "",
                    "placeholder": _("Type user name"),
                    "pattern": "^[A-z]{1}[_A-z0-9]{2,}$",
                }
            ),
            "password": PasswordInput(
                attrs={
                    "id": "id_new_password1",
                    "required": "",
                    "class": "form-control",
                    "placeholder": _("Type password"),
                    "onkeyup": "passwordForce(); if(beginCheckPassword1)checkPassExt();",
                }
            ),
            "groups": CheckboxSelectMultiple(),
        }

    def clean_password(self):
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


class UserFormUpdate(UserForm):
    password = CharField(
        required=False,
        widget=PasswordInput(
            attrs={
                "id": "id_new_password1",
                "class": "form-control",
                "placeholder": _("Type password"),
                "onkeyup": "passwordForce(); "
                "if(beginCheckPassword1) checkPassExt();",
            }
        ),
    )

    def clean_password(self):
        if self.cleaned_data["password"]:
            return make_password(self.cleaned_data["password"])
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
            self.add_error("email", _("E-mail is not registered"))
            self.add_error(None, _("E-mail is not registered"))
            return False


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["institution", "login_enabled", "citation_name"]

        widgets = {
            "institution": Select(attrs={"class": "form-control"}),
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
                    "autofocus": "true",
                    "required": "",
                    "placeholder": _("Type first name"),
                    "pattern": "^[A-z]{1,}([- ]{0,1}[A-z]{0,}){0,3}[A-z]$",
                }
            ),
            "last_name": TextInput(
                attrs={
                    "class": "form-control",
                    "autofocus": "true",
                    "required": "",
                    "placeholder": _("Type last name"),
                    "pattern": "^[A-z]{1,}([- ]{0,1}[A-z]{0,}){0,3}[A-z]$",
                }
            ),
            "email": TextInput(
                attrs={
                    "class": "form-control",
                    "required": "",
                    "placeholder": _("Type e-mail"),
                    "id": "id_email",
                    "type": "email",
                    "data-error": "E-mail inválido",
                    "pattern": "^[_A-Za-z0-9-\+]+(\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\.[A-Za-z0-9]+)*(\.[A-Za-z]{2,})$",
                }
            ),
            "citation_name": TextInput(
                attrs={"class": "form-control", "placeholder": _("Type citation name")}
            ),
        }


class InstitutionForm(ModelForm):
    class Meta:
        model = Institution
        fields = ["name", "acronym", "country", "parent"]

        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "required": "",
                    "autofocus": "",
                    "pattern": "^[A-z]{1,}([- ]{0,1}[A-z]{0,}){0,3}[A-z]$",
                }
            ),
            "acronym": TextInput(attrs={"class": "form-control"}),
            "country": Select(attrs={"class": "form-control"}),
            "parent": Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(InstitutionForm, self).__init__(*args, **kwargs)
        self.fields["country"].initial = "BR"
        instance = kwargs.get("instance") or self.instance

        if instance:
            parent_list = Institution.objects.all()
            parents_to_exclude = get_institutions_recursively(instance)
            for parent in parents_to_exclude:
                parent_list = parent_list.exclude(id=parent.id)
            self.fields["parent"].queryset = parent_list


def get_institutions_recursively(institution):
    institution_list = [institution]
    children = Institution.objects.filter(parent=institution)
    for child in children:
        if child not in institution_list:
            institution_list = get_institutions_recursively(child)
    return institution_list
