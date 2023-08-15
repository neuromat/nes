from django.contrib import admin
from plugin.models import RandomForests
from solo.admin import SingletonModelAdmin

admin.site.register(RandomForests, SingletonModelAdmin)
