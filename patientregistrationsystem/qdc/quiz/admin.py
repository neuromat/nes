from django.contrib import admin
from quiz.models import PersonalData,Patient, SchoolingOption, PaymentOption, ReligionOption, FleshToneOption, MaritalStatusOption, GenderOption

# Register your models here.
admin.site.register(Patient)
search_fields=['cpf_id']

admin.site.register(PersonalData)
admin.site.register(SchoolingOption)
admin.site.register(PaymentOption)
admin.site.register(ReligionOption)
admin.site.register(FleshToneOption)
admin.site.register(MaritalStatusOption)
admin.site.register(GenderOption)

