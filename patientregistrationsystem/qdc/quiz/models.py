
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from validation import CPF

# Create your models here.


def validate_cpf(value):
    validation = CPF(value)
    if not validation.isValid():
        #raise ValidationError(u'CPF %s não é válido' % value)
        raise ValidationError(_('CPF %s não é válido') % value)


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
    date_birth_txt = models.DateField(null=True, blank=True)
    gender_opt = models.ForeignKey(GenderOption, null=True, blank=True)
    marital_status_opt = models.ForeignKey(MaritalStatusOption, null=True, blank=True)

    class Meta:
        permissions = (
            ("view_patient", "Can view patient"),
        )

    def __unicode__(self):  # Python 3: def __str__(self):
        return \
            self.name_txt, self.cpf_id, self.rg_id, self.medical_record_number, self.natural_of_txt, \
            self.citizenship_txt, self.street_txt, self.zipcode_number, self.country_txt, self.state_txt, \
            self.city_txt, self.phone_number, self.cellphone_number, self.email_txt, self.date_birth_txt, \
            self.gender_opt, self.marital_status_opt


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
            self.id_patient, self.religion_opt, self.profession_txt, self.occupation_txt, bool(self.benefit_government_bool), \
            self.payment_opt, self.flesh_tone_opt, self.schooling_opt, self.tv_opt, self.dvd_opt, self.radio_opt, \
            self.bath_opt, self.automobile_opt, self.wash_machine_opt, self.refrigerator_opt, self.freezer_opt, \
            self.house_maid_opt, self.social_class_opt

    def calculate_social_class(self, **keywords):
        dictDvd = {'0': 0, '1': 2, '2': 2, '3': 2, '4': 2}
        dictBath = {'0': 0, '1': 4, '2': 5, '3': 6, '4': 7}
        dictAuto = {'0': 0, '1': 4, '2': 7, '3': 9, '4': 9}
        dictHousemaid = {'0': 0, '1': 3, '2': 4, '3': 4, '4': 4}
        dictRefrigerator = {'0': 0, '1': 4, '2': 4, '3': 4, '4': 4}
        dicScolarity = {'1': 0, '2': 1, '3': 2, '4': 4, '5': 8}
        points = 0

        for kw in keywords.keys():
            if kw == 'tv' or kw == 'radio':
                points += int(keywords[kw])
            elif kw == 'banheiro':
                points += dictBath[keywords[kw]]
            elif kw == 'automovel':
                points += dictAuto[keywords[kw]]
            elif kw == 'empregada':
                points += dictHousemaid[keywords[kw]]
            elif kw == 'dvd' or kw == 'maquina' or kw == 'freezer':
                points += dictDvd[keywords[kw]]
            elif kw == 'geladeira':
                points += dictRefrigerator[keywords[kw]]
            elif kw == 'escolaridade':
                points += dicScolarity[keywords[kw]]

        if points >= 0 and points <= 7:
            return 'E'
        elif points >= 8 and points <= 13:
            return 'D'
        elif points >= 14 and points <= 17:
            return 'C2'
        elif points >= 18 and points <= 22:
            return 'C1'
        elif points >= 23 and points <= 28:
            return 'B2'
        elif points >= 29 and points <= 34:
            return 'B1'
        elif points >= 35 and points <= 41:
            return 'A2'
        elif points >= 42 and points <= 46:
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
