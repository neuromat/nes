from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from modeltranslation.admin import TranslationAdmin

from experiment.models import Experiment, QuestionnaireResponse, StimulusType, FileFormat, \
    Manufacturer, Equipment, EEGElectrodeLocalizationSystem, EEGMachine, EEGFilterType, EEGAmplifier, EEGSolution, \
    EEGElectrodeNet, EEGElectrodeCap, EEGElectrodePosition, EEGElectrodeNetSystem, EEGCapSize, EEGElectrodeModel


admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)


class StimulusTypeAdmin(TranslationAdmin):
    pass


class FileFormatAdmin(TranslationAdmin):
    pass

admin.site.register(StimulusType, StimulusTypeAdmin)
admin.site.register(FileFormat, FileFormatAdmin)

admin.site.register(Manufacturer)
admin.site.register(Equipment)

admin.site.register(EEGMachine)
admin.site.register(EEGFilterType)
admin.site.register(EEGAmplifier)
admin.site.register(EEGSolution)
admin.site.register(EEGElectrodeNet)
admin.site.register(EEGElectrodeCap)
admin.site.register(EEGElectrodeLocalizationSystem)
admin.site.register(EEGElectrodePosition)
admin.site.register(EEGElectrodeNetSystem)
admin.site.register(EEGCapSize)
admin.site.register(EEGElectrodeModel)
