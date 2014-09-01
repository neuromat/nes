# -*- coding: UTF-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from quiz.models import Patient, User
from simple_history.models import HistoricalRecords

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
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("view_experiment", "Can view experiment"),
        )

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.title

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class QuestionnaireConfiguration(models.Model):
    lime_survey_id = models.IntegerField(null=False, blank=False)
    experiment = models.ForeignKey(Experiment, null=False, on_delete=models.PROTECT)
    number_of_fills = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    interval_between_fills_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    interval_between_fills_unit = models.ForeignKey(TimeUnit, null=True, blank=True)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.experiment.title + " - " + str(self.lime_survey_id)


class QuestionnaireResponse(models.Model):
    token_id = models.IntegerField(null=False)
    subject = models.ForeignKey(Subject, null=False)
    questionnaire_configuration = models.ForeignKey(QuestionnaireConfiguration, null=False, on_delete=models.PROTECT)
    date = models.DateField(default=datetime.date.today, null=False,
                                validators=[validate_date_questionnaire_response])
    questionnaire_responsible = models.ForeignKey(User, null=False)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("view_questionnaireresponse", "Can view questionnaire response"),
        )

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __unicode__(self):  # Python 3: def __str__(self):
        return "token id: " + str(self.token_id)

