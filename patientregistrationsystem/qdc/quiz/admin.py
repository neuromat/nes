from django.contrib import admin
from models import SchoolingOption, PaymentOption, ReligionOption, FleshToneOption, MaritalStatusOption, GenderOption, AmountCigarettesOption, AlcoholFrequencyOption, AlcoholPeriodOption

# Register your models here.
search_fields = ['cpf_id']

admin.site.register(SchoolingOption)
admin.site.register(PaymentOption)
admin.site.register(ReligionOption)
admin.site.register(FleshToneOption)
admin.site.register(MaritalStatusOption)
admin.site.register(GenderOption)
admin.site.register(AmountCigarettesOption)
admin.site.register(AlcoholFrequencyOption)
admin.site.register(AlcoholPeriodOption)

