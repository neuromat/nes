from django.db import models


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    eci_software = models.CharField(max_length=100, null=True, blank=True)
    questionnaires = models.ManyToManyField(Questionnaire, null=True, blank=True)


class Questionnaire(models.Model):
    sid = models.IntegerField(null=False, blank=False)