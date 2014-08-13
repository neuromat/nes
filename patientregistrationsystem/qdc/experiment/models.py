from django.db import models
from quiz.models import Patient


class Subject(models.Model):
    patient = models.ForeignKey(Patient)


class TimeUnit(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)


class Survey(models.Model):
    survey_id = models.IntegerField(null=False, blank=False)


class Questionnaire(models.Model):
    survey = models.ForeignKey(Survey, null=False)
    number_of_fills = models.IntegerField(null=False, blank=False)
    interval_between_fills_value = models.IntegerField(null=False, blank=False)
    interval_between_fills_unit = models.ForeignKey(TimeUnit, null=False)


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    questionnaires = models.ManyToManyField(Questionnaire, null=True)
    subjects = models.ManyToManyField(Subject, null=True)


class QuestionnaireResponse(models.Model):
    token = models.IntegerField(null=False, primary_key=True)
    subject = models.ForeignKey(Subject, null=False)
    experiment = models.ForeignKey(Experiment, null=False)
    questionnaire = models.ForeignKey(Questionnaire, null=False)
    # number_of_responses = models.IntegerField(null=False)
