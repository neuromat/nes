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

    #Audit trail - Simple History
    history = HistoricalRecords()
    #changed_by = models.ForeignKey('auth.User')

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


def get_dir(instance, filename):
    return "documents/%s/%s/%s" % (instance.experiment.id, instance.subject.id, filename)


class SubjectOfExperiment(models.Model):
    subject = models.ForeignKey(Subject, null=False, blank=False)
    experiment = models.ForeignKey(Experiment, null=False, blank=False)
    consent_form = models.FileField(upload_to=get_dir, null=True)

    class Meta:
        unique_together = ('subject', 'experiment',)


class QuestionnaireConfiguration(models.Model):
    lime_survey_id = models.IntegerField(null=False, blank=False)
    experiment = models.ForeignKey(Experiment, null=False, on_delete=models.PROTECT)
    number_of_fills = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    interval_between_fills_value = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    interval_between_fills_unit = models.ForeignKey(TimeUnit, null=True, blank=True)

    #Audit trail - Simple History
    history = HistoricalRecords()
    #changed_by = models.ForeignKey('auth.User')

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.experiment.title + " - " + str(self.lime_survey_id)

    class Meta:
        unique_together = ('lime_survey_id', 'experiment',)


class QuestionnaireResponse(models.Model):
    subject_of_experiment = models.ForeignKey(SubjectOfExperiment, null=False)
    questionnaire_configuration = models.ForeignKey(QuestionnaireConfiguration, null=False, on_delete=models.PROTECT)
    token_id = models.IntegerField(null=False)
    date = models.DateField(default=datetime.date.today, null=False,
                                validators=[validate_date_questionnaire_response])
    questionnaire_responsible = models.ForeignKey(User, null=False, related_name="+")

    #Audit trail - Simple History
    history = HistoricalRecords()
    #changed_by = models.ForeignKey('auth.User')

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
