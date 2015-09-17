from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from patient.models import Schooling, Payment, Religion, FleshTone, MaritalStatus, \
    Gender, AmountCigarettes, AlcoholFrequency, AlcoholPeriod, Patient, MedicalRecordData, \
    SocialDemographicData, SocialHistoryData


# Register your models here.
search_fields = ['cpf']

admin.site.register(Schooling)
admin.site.register(Payment)
admin.site.register(Religion)
admin.site.register(FleshTone)
admin.site.register(MaritalStatus)
admin.site.register(Gender)
admin.site.register(AmountCigarettes)
admin.site.register(AlcoholFrequency)
admin.site.register(AlcoholPeriod)

# Register models for Admin history and audit changes
admin.site.register(Patient, SimpleHistoryAdmin)
admin.site.register(SocialDemographicData, SimpleHistoryAdmin)
admin.site.register(SocialHistoryData, SimpleHistoryAdmin)
