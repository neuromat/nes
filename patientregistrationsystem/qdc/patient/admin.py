from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from simple_history.admin import SimpleHistoryAdmin

from .models import Schooling, Payment, Religion, FleshTone, MaritalStatus, \
    Gender, AmountCigarettes, AlcoholFrequency, AlcoholPeriod, Patient, \
    SocialDemographicData, SocialHistoryData, ClassificationOfDiseases

# Register your models here.
search_fields = ['cpf']

# Register models for Admin history and audit changes
admin.site.register(Patient, SimpleHistoryAdmin)
admin.site.register(SocialDemographicData, SimpleHistoryAdmin)
admin.site.register(SocialHistoryData, SimpleHistoryAdmin)


class SchoolingAdmin(TranslationAdmin):
    pass


class PaymentAdmin(TranslationAdmin):
    pass


class ReligionAdmin(TranslationAdmin):
    pass


class FleshToneAdmin(TranslationAdmin):
    pass


class MaritalStatusAdmin(TranslationAdmin):
    pass


class GenderAdmin(TranslationAdmin):
    pass


class AmountCigarettesAdmin(TranslationAdmin):
    pass


class AlcoholFrequencyAdmin(TranslationAdmin):
    pass


class AlcoholPeriodAdmin(TranslationAdmin):
    pass


class ClassificationOfDiseasesAdmin(TranslationAdmin):
    pass


admin.site.register(Schooling, SchoolingAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Religion, ReligionAdmin)
admin.site.register(FleshTone, FleshToneAdmin)
admin.site.register(MaritalStatus, MaritalStatusAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(AmountCigarettes, AmountCigarettesAdmin)
admin.site.register(AlcoholFrequency, AlcoholFrequencyAdmin)
admin.site.register(AlcoholPeriod, AlcoholPeriodAdmin)
admin.site.register(ClassificationOfDiseases, ClassificationOfDiseasesAdmin)
