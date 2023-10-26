from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Contact, LocalInstitution, UsefulLink

admin.site.register(Contact, SingletonModelAdmin)
admin.site.register(LocalInstitution, SingletonModelAdmin)
admin.site.register(UsefulLink)
