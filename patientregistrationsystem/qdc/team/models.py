from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Institution (models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=30, unique=True)
    country = models.CharField(max_length=30)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def __str__(self):
        return '%s' % (self.name)


class Person(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'))
    user = models.OneToOneField(User, null=True, blank=True, related_name='person')
    institution = models.ForeignKey(Institution, null=True, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Team(models.Model):
    name = models.CharField(max_length=150)
    acronym = models.CharField(max_length=20)


class TeamPerson(models.Model):
    team = models.ForeignKey(Team, related_name='team_persons')
    person = models.ForeignKey(Person, related_name='team_persons')
    is_coordinator = models.BooleanField()

    def __str__(self):
        return '%s %s - %s' % (self.person.first_name, self.person.last_name, self.team.name)
