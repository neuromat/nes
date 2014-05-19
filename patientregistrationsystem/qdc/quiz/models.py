
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals
from django.db import models


# Create your models here.


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

#class SocialClass(models.Model):
#    social_class_txt = models.CharField(max_length=50)
#    points = models.IntegerField

#    def __unicode__(self):
#        return self.social_class_txt

#    def calculateSocialClass(**keywords):
#        for kw in keywords.keys():
#            print kw, "-", keywords[kw]
#        #para cada item adicionar um valor na pontuacao

#   dicTV = {'TVoption0':'0', 'TVoption1' : '1', 'TVoption2' : '2', 'TVoption3' : '3' , 'TVoption4' : '4'}
#   dicDVD = {'DVDoption0':'0', 'DVDoption1' : '2', 'DVDoption2' : '2', 'DVDoption3' : '2' , 'DVDoption4' : '2'}
#   dicRadio = {'RADIOoption0':'0', 'RADIOoption1' : '1', 'RADIOoption2' : '2', 'RADIOoption3' : '3' , 'RADIOoption4' : '4'}
#   dicBath = {'Bathsoption0':'0', 'Bathsoption1' : '4', 'Bathsoption2' : '5', 'Bathsoption3' : '6' , 'Bathsoption4' : '7'}
#   dicAuto = {'Autooption0':'0', 'Autooption1' : '4', 'Autooption2' : '7', 'Autooption3' : '9' , 'Autooption4' : '9'}
#   dicHousemaid = {'Employoption0':'0', 'Employoption1' : '3', 'Employoption2' : '4', 'Employoption3' : '4' , 'Employoption4' : '4'}
#   dicWashMachine = {'WMoption0':'0', 'WMoption1' : '2', 'WMoption2' : '2', 'WMoption3' : '2' , 'WMoption4' : '2'}
#   dicRefrigerator = {'Refrigoption0':'0', 'Refrigoption1' : '4', 'Refrigoption2' : '4', 'Refrigoption3' : '4' , 'Refrigoption4' : '4'}
#   dicFreezer = {'Freezoption0':'0', 'Freezoption1' : '2', 'Freezoption2' : '2', 'Freezoption3' : '2' , 'Freezoption4' : '2'}

#chamada:
#calculateSocialClass(tvs='1', dvds='2', banheiros='3', ...)

class Patient(models.Model):
    cpf_id = models.CharField(null=True, blank=True, max_length=15, unique=True)
    rg_id = models.CharField(max_length=15, null=True, blank=True)
    name_txt = models.CharField(max_length=50)
    nr_record = models.AutoField(primary_key=True)
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
    dt_birth_txt = models.DateField(null=True, blank=True)
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
            self.city_txt, self.phone_number, self.cellphone_number, self.email_txt, self.dt_birth_txt, \
            self.gender_opt, self.marital_status_opt


class SocialDemographicData(models.Model):
    id_patient = models.ForeignKey(Patient)
    religion_opt = models.ForeignKey(ReligionOption, null=True, blank=True)
    profession_txt = models.CharField(null=True, blank=True, max_length=50)
    occupation_txt = models.CharField(null=True, blank=True, max_length=50)
    benefit_gov_bool = models.CharField(null=True, blank=True, max_length=10)
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
    # social_class_opt = models.ForeignKey(SocialClass)

    def __unicode__(self):
        return \
            self.id_patient, self.religion_opt, self.profession_txt, self.occupation_txt, bool(self.benefit_gov_bool), \
            self.payment_opt, self.flesh_tone_opt, self.schooling_opt, self.tv_opt, self.dvd_opt, self.radio_opt, \
            self.bath_opt, self.automobile_opt, self.wash_machine_opt, self.refrigerator_opt, self.freezer_opt, \
            self.house_maid_opt


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
