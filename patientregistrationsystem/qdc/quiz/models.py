# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from quiz.validation import CPF

import datetime


# Valida CPF
def validate_cpf(value):
    validation = CPF(value)
    if not validation.isValid():
        # raise ValidationError(u'CPF %s não é válido' % value)
        raise ValidationError(_('CPF %s não é válido') % value)


# Valida data de nascimento:
# data de nascimento maior que a data atual
def validate_date_birth(value):
    if value > datetime.date.today():
        raise ValidationError(_('Data de nascimento não pode ser maior que a data de hoje.'))


class Payment(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class FleshTone(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class MaritalStatus(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class Religion(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class Schooling(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class AmountCigarettes(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class AlcoholFrequency(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class AlcoholPeriod(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Patient(models.Model):
    cpf = models.CharField(null=True, blank=True, max_length=15, unique=True, validators=[validate_cpf])
    rg = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=50)
    medical_record = models.CharField(max_length=25, null=True, blank=True)
    natural_of = models.CharField(max_length=50, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    address_number = models.IntegerField(max_length=6, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    address_complement = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=12, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    cellphone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    date_birth = models.DateField(null=False, blank=False, validators=[validate_date_birth])
    gender = models.ForeignKey(Gender, null=False, blank=False)
    marital_status = models.ForeignKey(MaritalStatus, null=True, blank=True)
    removed = models.BooleanField(null=False, default=False)

    # Audit trail
    history = HistoricalRecords()
    changed_by = models.ForeignKey('auth.User')

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    class Meta:
        permissions = (
            ("view_patient", "Can view patient"),
        )

    def get_absolute_url(self):
        return "/quiz/patient/%i/" % self.pk

    def __unicode__(self):  # Python 3: def __str__(self):
        return \
            self.name


class SocialDemographicData(models.Model):
    patient = models.ForeignKey(Patient)
    religion = models.ForeignKey(Religion, null=True, blank=True)
    profession = models.CharField(null=True, blank=True, max_length=50)
    occupation = models.CharField(null=True, blank=True, max_length=50)
    benefit_government = models.NullBooleanField(blank=True)
    payment = models.ForeignKey(Payment, null=True, blank=True)
    flesh_tone = models.ForeignKey(FleshTone, null=True, blank=True)
    schooling = models.ForeignKey(Schooling, null=True, blank=True)
    tv = models.IntegerField(null=True, blank=True, )
    dvd = models.IntegerField(null=True, blank=True, )
    radio = models.IntegerField(null=True, blank=True, )
    bath = models.IntegerField(null=True, blank=True, )
    automobile = models.IntegerField(null=True, blank=True, )
    wash_machine = models.IntegerField(null=True, blank=True, )
    refrigerator = models.IntegerField(null=True, blank=True, )
    freezer = models.IntegerField(null=True, blank=True, )
    house_maid = models.IntegerField(null=True, blank=True, )
    social_class = models.CharField(null=True, blank=True, max_length=10)

    # Changes to audit trail
    history = HistoricalRecords()
    changed_by = models.ForeignKey('auth.User')

    def __unicode__(self):
        return \
            str(self.patient)

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    @staticmethod
    def calculate_social_class(**keywords):
        dict_dvd = {'0': 0, '1': 2, '2': 2, '3': 2, '4': 2}
        dict_bath = {'0': 0, '1': 4, '2': 5, '3': 6, '4': 7}
        dict_auto = {'0': 0, '1': 4, '2': 7, '3': 9, '4': 9}
        dict_housemaid = {'0': 0, '1': 3, '2': 4, '3': 4, '4': 4}
        dict_refrigerator = {'0': 0, '1': 4, '2': 4, '3': 4, '4': 4}
        dict_schooling = {'1': 0, '2': 1, '3': 2, '4': 4, '5': 8}
        points = 0

        for kw in keywords.keys():
            if kw == 'tv' or kw == 'radio':
                points += int(keywords[kw])
            elif kw == 'banheiro':
                points += dict_bath[keywords[kw]]
            elif kw == 'automovel':
                points += dict_auto[keywords[kw]]
            elif kw == 'empregada':
                points += dict_housemaid[keywords[kw]]
            elif kw == 'dvd' or kw == 'maquina' or kw == 'freezer':
                points += dict_dvd[keywords[kw]]
            elif kw == 'geladeira':
                points += dict_refrigerator[keywords[kw]]
            elif kw == 'escolaridade':
                points += dict_schooling[keywords[kw]]

        if 0 <= points <= 7:
            return 'E'
        elif 8 <= points <= 13:
            return 'D'
        elif 14 <= points <= 17:
            return 'C2'
        elif 18 <= points <= 22:
            return 'C1'
        elif 23 <= points <= 28:
            return 'B2'
        elif 29 <= points <= 34:
            return 'B1'
        elif 35 <= points <= 41:
            return 'A2'
        elif 42 <= points <= 46:
            return 'A1'
        else:
            return ''


class SocialHistoryData(models.Model):
    patient = models.ForeignKey(Patient)
    smoker = models.NullBooleanField(blank=True)
    amount_cigarettes = models.ForeignKey(AmountCigarettes, null=True, blank=True, default=0)
    ex_smoker = models.NullBooleanField(blank=True)
    alcoholic = models.NullBooleanField(blank=True)
    alcohol_frequency = models.ForeignKey(AlcoholFrequency, null=True, blank=True, default=0)
    alcohol_period = models.ForeignKey(AlcoholPeriod, null=True, blank=True, default=0)
    drugs = models.CharField(max_length=25, null=True, blank=True)

    # Audit trail
    history = HistoricalRecords()
    changed_by = models.ForeignKey('auth.User')

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __unicode__(self):
        return \
            str(self.patient)


class MedicalRecordData(models.Model):
    patient = models.ForeignKey(Patient, null=False)
    record_date = models.DateTimeField(null=False, auto_now_add=True)
    record_responsible = models.ForeignKey(User, null=False)

    class Meta:
        permissions = (
            ("view_medicalrecorddata", "Can view medical record"),
        )

    def __unicode__(self):
        return \
            self.patient, self.record_date, self.record_responsible


class ClassificationOfDiseases(models.Model):
    code = models.CharField(max_length=10, null=False)
    description = models.CharField(max_length=300, null=False)
    abbreviated_description = models.CharField(max_length=100, null=False)
    parent = models.ForeignKey('self', null=True, related_name='children')

    def __unicode__(self):
        return self.abbreviated_description


class Diagnosis(models.Model):
    medical_record_data = models.ForeignKey(MedicalRecordData, null=False)
    classification_of_diseases = models.ForeignKey(ClassificationOfDiseases, null=False)
    date = models.DateField(null=True)
    description = models.CharField(max_length=300, null=True)

    class Meta:
        unique_together = ('medical_record_data', 'classification_of_diseases',)

    def __unicode__(self):
        return unicode(self.classification_of_diseases), self.date, self.description


class ComplementaryExam(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    doctor = models.CharField(max_length=50, null=True, blank=True)
    doctor_register = models.CharField(max_length=10, null=True, blank=True)
    exam_site = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.description)


def get_user_dir(instance, filename):
    # return 'images/%s/%s' % (instance.user.user.username, filename)
    return "exams/%s/%s/%s" % (instance.exam.diagnosis.medical_record_data.patient.pk, instance.exam.pk, filename)


class ExamFile(models.Model):
    exam = models.ForeignKey(ComplementaryExam, null=False)
    content = models.FileField(upload_to=get_user_dir, null=False)

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(ExamFile, self).delete(*args, **kwargs)
