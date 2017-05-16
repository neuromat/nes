from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Contact, LocalInstitution

admin.site.register(Contact, SingletonModelAdmin)
admin.site.register(LocalInstitution, SingletonModelAdmin)
