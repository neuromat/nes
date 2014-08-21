# -*- coding: UTF-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from quiz.models import Patient, User

import datetime


def validate_date_questionnaire_response(value):
    if value > datetime.date.today():
        raise ValidationError('Data de preenchimento não pode ser maior que a data de hoje.')

class Subject(models.Model):
    patient = models.ForeignKey(Patient)


class TimeUnit(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Experiment(models.Model):
    title = models.CharField(null=False, max_length=50, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)
    subjects = models.ManyToManyField(Subject, null=True)

    class Meta:
        permissions = (
            ("view_experiment", "Can view experiment"),
        )


class QuestionnaireConfiguration(models.Model):
    lime_survey_id = models.IntegerField(null=False, blank=False)
    experiment = models.ForeignKey(Experiment, null=False)
    number_of_fills = models.IntegerField(null=True, blank=True)
    interval_between_fills_value = models.IntegerField(null=True, blank=True)
    interval_between_fills_unit = models.ForeignKey(TimeUnit, null=True, blank=True)


class QuestionnaireResponse(models.Model):
    token_id = models.IntegerField(null=False, primary_key=True)
    subject = models.ForeignKey(Subject, null=False)
    questionnaire_configuration = models.ForeignKey(QuestionnaireConfiguration, null=False)
    date = models.DateField(default=datetime.date.today, null=False,
                                validators=[validate_date_questionnaire_response])
    questionnaire_responsible = models.ForeignKey(User, null=False)

    class Meta:
        permissions = (
            ("view_questionnaireresponse", "Can view questionnaire response"),
        )

