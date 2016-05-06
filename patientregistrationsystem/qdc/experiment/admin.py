from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from modeltranslation.admin import TranslationAdmin

from experiment.models import Experiment, QuestionnaireResponse, StimulusType, FileFormat, \
    Manufacturer, Equipment, EquipmentModel, EquipmentCategory

admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)


class StimulusTypeAdmin(TranslationAdmin):
    pass


admin.site.register(StimulusType, StimulusTypeAdmin)
admin.site.register(FileFormat)

admin.site.register(Manufacturer)
admin.site.register(Equipment)
admin.site.register(EquipmentModel)
admin.site.register(EquipmentCategory)
