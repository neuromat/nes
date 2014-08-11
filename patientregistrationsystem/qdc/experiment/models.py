from django.db import models
from quiz.models import Patient


class Subject(models.Model):
    patient = models.ForeignKey(Patient)


class Questionnaire(models.Model):
    survey_id = models.IntegerField(null=False, blank=False)


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    # start_date = models.DateField(null=True, blank=True)
    # end_date = models.DateField(null=True, blank=True)
    # eci_software = models.CharField(max_length=100, null=True, blank=True)
    questionnaires = models.ManyToManyField(Questionnaire, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, null=True, blank=True)


class QuestionnaireResponse(models.Model):
    token = models.IntegerField(null=False, primary_key=True)
    subject = models.ForeignKey(Subject, null=False)
    experiment = models.ForeignKey(Experiment, null=False)
    questionnaire = models.ForeignKey(Questionnaire, null=False)
    number_of_responses = models.IntegerField(null=False)
