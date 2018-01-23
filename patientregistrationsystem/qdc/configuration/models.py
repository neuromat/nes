from django.db import models
from solo.models import SingletonModel
from team.models import Institution as TeamInstitution


def get_institution_logo_dir(instance, filename):
    return "institution_logo/%s/%s" % (instance.id, filename)


class LocalInstitution(SingletonModel):
    code = models.CharField(max_length=150, null=True, blank=True)
    institution = models.ForeignKey(TeamInstitution)
    url = models.URLField(null=True, blank=True)
    logo = models.FileField(upload_to=get_institution_logo_dir, null=True, blank=True)


class Contact(SingletonModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class RightsSupport(models.Model):

    class Meta:

        managed = False

        permissions = (
            ('upgrade_rights', 'NES administrator rights'),
        )

