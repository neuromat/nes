from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from modeltranslation.admin import TranslationAdmin

from experiment.models import Experiment, QuestionnaireResponse, StimulusType, FileFormat, Tag, \
    Software, SoftwareVersion, ADConverter, \
    StandardizationSystem, EMGIntramuscularPlacement, EMGSurfacePlacement, EMGNeedlePlacement, \
    Muscle, MuscleSubdivision, MuscleSide

admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)


class StimulusTypeAdmin(TranslationAdmin):
    pass


class FileFormatAdmin(TranslationAdmin):
    pass

admin.site.register(StimulusType, StimulusTypeAdmin)
admin.site.register(FileFormat, FileFormatAdmin)
admin.site.register(Tag)
admin.site.register(Software)
admin.site.register(SoftwareVersion)
admin.site.register(ADConverter)
admin.site.register(StandardizationSystem)
admin.site.register(EMGIntramuscularPlacement)
admin.site.register(EMGSurfacePlacement)
admin.site.register(EMGNeedlePlacement)
admin.site.register(Muscle)
admin.site.register(MuscleSubdivision)
admin.site.register(MuscleSide)
