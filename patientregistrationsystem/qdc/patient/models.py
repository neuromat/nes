# -*- coding: UTF-8 -*-

import datetime
import random

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

from survey.models import Survey

from .validation import CPF


def validate_date_questionnaire_response(value):
    if value > datetime.date.today():
        raise ValidationError(_("Fill date can not be bigger than today's date."))


# Valida CPF
def validate_cpf(value):
    validation = CPF(value)
    if not validation.isValid():
        # raise ValidationError(u'CPF %s não é válido' % value)
        raise ValidationError(_('CPF %(CPF)s invalid') % {"CPF": value})


# Valida data de nascimento:
# data de nascimento maior que a data atual
def validate_date_birth(value):
    if value > datetime.date.today():
        raise ValidationError(_("Date of birth can't be greater than today date."))


class Payment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class FleshTone(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class MaritalStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Religion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Schooling(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class AmountCigarettes(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class AlcoholFrequency(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AlcoholPeriod(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Patient(models.Model):
    code = models.CharField(max_length=10, null=False, unique=True)

    name = models.CharField(max_length=50)
    cpf = models.CharField(null=True, blank=True, max_length=15, unique=True, validators=[validate_cpf])
    origin = models.CharField(max_length=50, null=True, blank=True)
    medical_record = models.CharField(max_length=25, null=True, blank=True)
    date_birth = models.DateField(null=False, blank=False, validators=[validate_date_birth])
    gender = models.ForeignKey(Gender, null=False, blank=False)
    rg = models.CharField(max_length=15, null=True, blank=True)
    marital_status = models.ForeignKey(MaritalStatus, null=True, blank=True)

    country = models.CharField(max_length=30, null=True, blank=True)
    zipcode = models.CharField(max_length=12, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    address_number = models.IntegerField(null=True, blank=True)
    address_complement = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

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
            ("export_patient", "Can export patient"),
            ("sensitive_data_patient", "Can view sensitive patient data"),
        )

    def get_absolute_url(self):
        return "/patient/%i/" % self.pk

    def __str__(self):
        return \
            self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.create_random_patient_code()
        super(Patient, self).save(*args, **kwargs)

    @staticmethod
    def create_random_patient_code():
        used_codes = set([patient.code for patient in Patient.objects.all()])
        possible_code = set(['P' + str(item) for item in range(1, 100000)])
        available_codes = list(possible_code - used_codes)
        return random.choice(available_codes)


class Telephone(models.Model):
    patient = models.ForeignKey(Patient)
    number = models.CharField(max_length=15)

    MOBILE = 'MO'
    HOME = 'HO'
    WORK = 'WO'
    MAIN = 'MA'
    FAX_WORK = 'FW'
    FAX_HOME = 'FH'
    PAGER = 'PA'
    OTHER = 'OT'
    TYPE_CHOICES = ((MOBILE, _("Cell phone")),
                    (HOME, _("Home phone")),
                    (WORK, _("Business")),
                    (MAIN, _("Main")),
                    (FAX_WORK, _("Business fax")),
                    (FAX_HOME, _("Home fax")),
                    (PAGER, _("Pager")),
                    (OTHER, _("Other")))

    type = models.CharField(max_length=15, choices=TYPE_CHOICES, blank=True)
    note = models.CharField(max_length=50, blank=True)

    # Audit trail
    history = HistoricalRecords()
    changed_by = models.ForeignKey('auth.User')

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.number + '(' + self.type + ') - ' + self.note


class SocialDemographicData(models.Model):
    patient = models.ForeignKey(Patient)
    natural_of = models.CharField(max_length=50, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
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

    def __str__(self):
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
        #  According to IBGE:
        punctuation_table = {
            'tv':           {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
            'radio':        {0: 0, 1: 1, 2: 2, 3: 3, 4: 4},

            'dvd':          {0: 0, 1: 2, 2: 2, 3: 2, 4: 2},
            'wash_mashine': {0: 0, 1: 2, 2: 2, 3: 2, 4: 2},
            'freezer':      {0: 0, 1: 2, 2: 2, 3: 2, 4: 2},

            'bath':         {0: 0, 1: 4, 2: 5, 3: 6, 4: 7},
            'car':          {0: 0, 1: 4, 2: 7, 3: 9, 4: 9},
            'housemaid':    {0: 0, 1: 3, 2: 4, 3: 4, 4: 4},
            'refrigerator': {0: 0, 1: 4, 2: 4, 3: 4, 4: 4},

            'schooling':    {'1': 0, '2': 1, '3': 2, '4': 4, '5': 8}
        }
        points = 0

        for key_word in list(keywords.keys()):
            points += (punctuation_table[key_word])[keywords[key_word]]

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

    def __str__(self):
        return \
            str(self.patient)


class MedicalRecordData(models.Model):
    patient = models.ForeignKey(Patient, null=False)
    record_date = models.DateTimeField(null=False, auto_now_add=True)
    record_responsible = models.ForeignKey(User, null=False)

    class Meta:
        permissions = (
            ("view_medicalrecorddata", "Can view medical record"),
            ("export_medicalrecorddata", "Can export medical record"),
        )

    def __str__(self):
        return \
            self.patient, self.record_date, self.record_responsible


class ClassificationOfDiseases(models.Model):
    code = models.CharField(max_length=10, null=False)
    description = models.CharField(max_length=300, null=False)
    abbreviated_description = models.CharField(max_length=190, null=False)
    parent = models.ForeignKey('self', null=True, related_name='children')

    def __str__(self):
        return self.abbreviated_description


class Diagnosis(models.Model):
    medical_record_data = models.ForeignKey(MedicalRecordData, null=False)
    classification_of_diseases = models.ForeignKey(ClassificationOfDiseases, null=False)
    date = models.DateField(null=True)
    description = models.CharField(max_length=300, null=True)

    class Meta:
        unique_together = ('medical_record_data', 'classification_of_diseases',)

    def __str__(self):
        return str(self.classification_of_diseases), self.date, self.description


class ComplementaryExam(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    doctor = models.CharField(max_length=50, null=True, blank=True)
    doctor_register = models.CharField(max_length=10, null=True, blank=True)
    exam_site = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.description)


def get_user_dir(instance, filename):
    return "exams/%(patient)s/%(exam)s/%(filename)s" % \
        {'patient': instance.exam.diagnosis.medical_record_data.patient.pk,
         'exam': instance.exam.pk, 'filename': filename}


class ExamFile(models.Model):
    exam = models.ForeignKey(ComplementaryExam, null=False)
    content = models.FileField(upload_to=get_user_dir, null=False)

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(ExamFile, self).delete(*args, **kwargs)


class QuestionnaireResponse(models.Model):
    patient = models.ForeignKey(Patient, null=False)

    survey = models.ForeignKey(Survey, null=False, on_delete=models.PROTECT)

    token_id = models.IntegerField(null=False)
    date = models.DateField(default=datetime.date.today, null=False, validators=[validate_date_questionnaire_response])
    questionnaire_responsible = models.ForeignKey(User, null=False, related_name="+")

    class Meta:
        permissions = (
            ("view_questionnaireresponse", "Can view questionnaire response"),
            ("export_questionnaireresponse", "Can export questionnaire response"),
        )

    def __str__(self):
        return _("token id: ") + str(self.token_id)
