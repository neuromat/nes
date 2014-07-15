
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from validation import CPF
import datetime
from django.core.files.storage import FileSystemStorage
import patched_locks


#Valida CPF
def validate_cpf(value):
    validation = CPF(value)
    if not validation.isValid():
        # raise ValidationError(u'CPF %s não é válido' % value)
        raise ValidationError(_('CPF %s não é válido') % value)


#Valida data de nascimento:
#data de nascimento maior que a data atual
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

    class Meta:
        permissions = (
            ("view_patient", "Can view patient"),
        )

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

    def __unicode__(self):
        return \
            self.id_patient, self.religion_opt, self.profession_txt, self.occupation_txt, bool(
                self.benefit_government_bool), \
            self.payment_opt, self.flesh_tone_opt, self.schooling_opt, self.tv_opt, self.dvd_opt, self.radio_opt, \
            self.bath_opt, self.automobile_opt, self.wash_machine_opt, self.refrigerator_opt, self.freezer_opt, \
            self.house_maid_opt, self.social_class_opt

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

    def __unicode__(self):
        return \
            self.id_patient, bool(self.smoker), self.amount_cigarettes_opt, bool(self.ex_smoker), bool(self.alcoholic),\
            self.alcohol_frequency_opt, self.alcohol_period_opt, self.drugs_opt


class Side(models.Model):
    description = models.CharField(max_length=10, null=False)

    def __unicode__(self):
        return self.description


class CervicalVertebrae(models.Model):
    code = models.CharField(max_length=2, null=False)

    def __unicode__(self):
        return self.code

class ThoracicVertebrae(models.Model):
    code = models.CharField(max_length=3, null=False)

    def __unicode__(self):
        return self.code


class LumbosacralVertebrae(models.Model):
    code = models.CharField(max_length=2, null=False)

    def __unicode__(self):
        return self.code


class PainLocalization(models.Model):
    pain_localization = models.CharField(max_length=50, null=False)

    def __unicode__(self):
        return self.pain_localization


class MedicalRecordData(models.Model):
    patient = models.ForeignKey(Patient, null=False)
    record_date = models.DateTimeField(null=False, auto_now_add=True)
    record_responsible = models.ForeignKey(User, null=False)

    fracture_history = models.CharField(max_length=10, null=True, blank=True)
    scapula_fracture_side = models.ForeignKey(Side, related_name='side_scapula_fracture', null=True, blank=True)
    clavicle_fracture_side = models.ForeignKey(Side, related_name='side_clavicle_fracture', null=True, blank=True)
    rib_fracture = models.CharField(max_length=10, null=True, blank=True)
    cervical_vertebrae_fracture = models.ManyToManyField(CervicalVertebrae, blank=True, null=True)
    thoracic_vertebrae_fracture = models.ManyToManyField(ThoracicVertebrae, blank=True, null=True)
    lumbosacral_vertebrae_fracture = models.ManyToManyField(LumbosacralVertebrae, blank=True, null=True)
    superior_members_fracture_side = \
        models.ForeignKey(Side, related_name='side_superior_members_fracture', null=True, blank=True)
    inferior_members_fracture_side = \
        models.ForeignKey(Side, related_name='side_inferior_members_fracture', null=True, blank=True)
    pelvis_fracture_side = \
        models.ForeignKey(Side, related_name='side_pelvis_fracture', null=True, blank=True)

    orthopedic_surgery = models.CharField(max_length=10, null=True, blank=True)
    scapula_surgery_side = models.ForeignKey(Side, related_name='side_scapula_surgery', null=True, blank=True)
    clavicle_surgery_side = models.ForeignKey(Side, related_name='side_clavicle_surgery', null=True, blank=True)
    rib_surgery = models.CharField(max_length=10, null=True, blank=True)
    cervical_vertebrae_surgery = models.CharField(max_length=10, null=True, blank=True)
    thoracic_vertebrae_surgery = models.CharField(max_length=10, null=True, blank=True)
    lumbosacral_vertebrae_surgery = models.CharField(max_length=10, null=True, blank=True)
    superior_members_surgery_side = \
        models.ForeignKey(Side, related_name='side_superior_members_surgery', null=True, blank=True)
    inferior_members_surgery_side = \
        models.ForeignKey(Side, related_name='side_inferior_members_surgery', null=True, blank=True)
    pelvis_surgery_side = \
        models.ForeignKey(Side, related_name='side_pelvis_surgery', null=True, blank=True)

    nerve_surgery = models.CharField(max_length=10, null=True, blank=True)
    nerve_surgery_type = models.CharField(max_length=50, null=True, blank=True)

    vertigo_history = models.CharField(max_length=10, null=True, blank=True)
    pain_localizations = models.ManyToManyField(PainLocalization, related_name="medical_records")
    headache = models.CharField(max_length=10, null=True, blank=True)
    hypertension = models.CharField(max_length=10, null=True, blank=True)
    diabetes = models.CharField(max_length=10, null=True, blank=True)
    hormonal_dysfunction = models.CharField(max_length=10, null=True, blank=True)

    def __unicode__(self):
        return \
            self.patient, self.record_date, self.record_responsible, self.fracture_history, self.scapula_fracture_side,\
            self.clavicle_fracture_side, self.rib_fracture, self.cervical_vertebrae_fracture, self.thoracic_vertebrae_fracture,\
            self.lumbosacral_vertebrae_fracture, self.superior_members_fracture_side, self.inferior_members_fracture_side,\
            self.pelvis_fracture_side, self.orthopedic_surgery, self.scapula_surgery_side, self.clavicle_surgery_side,\
            self.rib_surgery, self.cervical_vertebrae_surgery, self.thoracic_vertebrae_surgery, self.lumbosacral_vertebrae_surgery,\
            self.superior_members_surgery_side, self.inferior_members_surgery_side, self.pelvis_surgery_side,\
            self.nerve_surgery, self.nerve_surgery_type, self.vertigo_history, self.pain_localizations,\
            self.headache, self.hypertension, self.hormonal_dysfunction, self.diabetes


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

    def __unicode__(self):
        return unicode(self.classification_of_diseases)


class ComplementaryExam(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    description = models.CharField(max_length=50, null=False, blank=False)
    doctor = models.CharField(max_length=50, null=False, blank=False)
    doctor_register = models.CharField(max_length=10, null=False, blank=False)
    exam_site = models.CharField(max_length=100, null=False, blank=False)

    def __unicode__(self):
        return unicode(self.description)


class ExamFile (models.Model):
    exam = models.ForeignKey(ComplementaryExam, null=False)
    content = models.FileField(upload_to="documents")
