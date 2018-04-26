from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Institution (models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=30, unique=True)
    country = models.CharField(max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return '%s' % self.name


class Person(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'))
    user = models.OneToOneField(User, null=True, blank=True, related_name='person')
    institution = models.ForeignKey(Institution, null=True, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
