from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from modeltranslation.admin import TranslationAdmin

from experiment.models import Experiment, QuestionnaireResponse, StimulusType, FileFormat, Tag, \
    Software, SoftwareVersion, ADConverter

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
