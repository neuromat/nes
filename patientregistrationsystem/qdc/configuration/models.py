from typing import Any
from django.db.models.base import ModelBase
from custom_user.models import Institution
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta
from solo.models import SingletonModel


def get_institution_logo_dir(instance: Any, filename: str) -> str:
    return "institution_logo/%s/%s" % (instance.id, filename)


class LocalInstitution(SingletonModel):
    code = models.CharField(max_length=150, null=True, blank=True)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, null=True, blank=True
    )

    url = models.URLField(null=True, blank=True)
    logo = models.FileField(upload_to=get_institution_logo_dir, null=True, blank=True)

    def __str__(self) -> str:
        return "Local Institution"

    class Meta(TypedModelMeta):
        verbose_name = "Local Institution"


class Contact(SingletonModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self) -> str:
        return "%s" % self.name

    class Meta(TypedModelMeta):
        verbose_name = "Contact"


class RightsSupport(models.Model):
    class Meta(TypedModelMeta):
        managed = False

        permissions = [
            ("upgrade_rights", "Can upgrade NES version"),
        ]
