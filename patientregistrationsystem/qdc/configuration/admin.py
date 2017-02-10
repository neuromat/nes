from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import Contact, Institution

admin.site.register(Contact, SingletonModelAdmin)
admin.site.register(Institution, SingletonModelAdmin)
