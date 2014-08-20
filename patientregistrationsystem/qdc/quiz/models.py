# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from validation import CPF
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
        raise ValidationError('Data de nascimento não pode ser maior que a data de hoje.')


class PaymentOption(models.Model):
    payment_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.payment_txt


class GenderOption(models.Model):
    gender_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.gender_txt


class FleshToneOption(models.Model):
    flesh_tone_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.flesh_tone_txt


class MaritalStatusOption(models.Model):
    marital_status_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.marital_status_txt


class ReligionOption(models.Model):
    religion_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.religion_txt


class SchoolingOption(models.Model):
    schooling_txt = models.CharField(max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.schooling_txt


class AmountCigarettesOption(models.Model):
    amount_cigarettes_txt = models.CharField(max_length=50)

    def __unicode__(self):
        return self.amount_cigarettes_txt


class AlcoholFrequencyOption(models.Model):
    alcohol_frequency_txt = models.CharField(max_length=100)

    def __unicode__(self):
        return self.alcohol_frequency_txt


class AlcoholPeriodOption(models.Model):
    alcohol_period_txt = models.CharField(max_length=50)

    def __unicode__(self):
        return self.alcohol_period_txt


class Patient(models.Model):
    cpf_id = models.CharField(null=True, blank=True, max_length=15, unique=True, validators=[validate_cpf])
    rg_id = models.CharField(max_length=15, null=True, blank=True)
    name_txt = models.CharField(max_length=50)
    number_record = models.AutoField(primary_key=True)
    medical_record_number = models.CharField(max_length=25, null=True, blank=True)
    natural_of_txt = models.CharField(max_length=50, null=True, blank=True)
    citizenship_txt = models.CharField(max_length=50, null=True, blank=True)
    street_txt = models.CharField(max_length=50, null=True, blank=True)
    number = models.IntegerField(max_length=6, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    complement = models.CharField(max_length=50, null=True, blank=True)
    zipcode_number = models.CharField(max_length=12, null=True, blank=True)
    country_txt = models.CharField(max_length=30, null=True, blank=True)
    state_txt = models.CharField(max_length=30, null=True, blank=True)
    city_txt = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    cellphone_number = models.CharField(max_length=15, null=True, blank=True)
    email_txt = models.EmailField(null=True, blank=True)
    date_birth_txt = models.DateField(null=False, blank=False, validators=[validate_date_birth])
    gender_opt = models.ForeignKey(GenderOption, null=False, blank=False)
    marital_status_opt = models.ForeignKey(MaritalStatusOption, null=True, blank=True)
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
            self.name_txt


class SocialDemographicData(models.Model):
    id_patient = models.ForeignKey(Patient)
    religion_opt = models.ForeignKey(ReligionOption, null=True, blank=True)
    profession_txt = models.CharField(null=True, blank=True, max_length=50)
    occupation_txt = models.CharField(null=True, blank=True, max_length=50)
    benefit_government_bool = models.CharField(null=True, blank=True, max_length=10)
    payment_opt = models.ForeignKey(PaymentOption, null=True, blank=True)
    flesh_tone_opt = models.ForeignKey(FleshToneOption, null=True, blank=True)
    schooling_opt = models.ForeignKey(SchoolingOption, null=True, blank=True)
    tv_opt = models.IntegerField(null=True, blank=True, )
    dvd_opt = models.IntegerField(null=True, blank=True, )
    radio_opt = models.IntegerField(null=True, blank=True, )
    bath_opt = models.IntegerField(null=True, blank=True, )
    automobile_opt = models.IntegerField(null=True, blank=True, )
    wash_machine_opt = models.IntegerField(null=True, blank=True, )
    refrigerator_opt = models.IntegerField(null=True, blank=True, )
    freezer_opt = models.IntegerField(null=True, blank=True, )
    house_maid_opt = models.IntegerField(null=True, blank=True, )
    social_class_opt = models.CharField(null=True, blank=True, max_length=10)

    # Changes to audit trail
    history = HistoricalRecords()
    changed_by = models.ForeignKey('auth.User')

    def __unicode__(self):
        return \
            str(self.id_patient)

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
        dict_scholarity = {'1': 0, '2': 1, '3': 2, '4': 4, '5': 8}
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
                points += dict_scholarity[keywords[kw]]

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
    id_patient = models.ForeignKey(Patient)
    smoker = models.CharField(max_length=10, null=True, blank=True)
    amount_cigarettes_opt = models.ForeignKey(AmountCigarettesOption, null=True, blank=True, default=0)
    ex_smoker = models.CharField(max_length=10, null=True, blank=True)
    alcoholic = models.CharField(max_length=10, null=True, blank=True)
    alcohol_frequency_opt = models.ForeignKey(AlcoholFrequencyOption, null=True, blank=True, default=0)
    alcohol_period_opt = models.ForeignKey(AlcoholPeriodOption, null=True, blank=True, default=0)
    drugs_opt = models.CharField(max_length=25, null=True, blank=True)

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
            str(self.id_patient)


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
    return "documents/%s/%s/%s" % (instance.exam.diagnosis.medical_record_data.patient.pk, instance.exam.pk, filename)


class ExamFile(models.Model):
    exam = models.ForeignKey(ComplementaryExam, null=False)
    content = models.FileField(upload_to=get_user_dir, null=False)

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(ExamFile, self).delete(*args, **kwargs)
