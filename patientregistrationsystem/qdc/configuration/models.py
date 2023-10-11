from os import name
from typing import LiteralString
from custom_user.models import Institution
from django.db import models
from solo.models import SingletonModel
from django_stubs_ext.db.models import TypedModelMeta


def get_institution_logo_dir(instance, filename) -> LiteralString:
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


class RightsSupport(models.Model):
    class Meta:
        managed = False

        permissions = (("upgrade_rights", "Can upgrade NES version"),)
