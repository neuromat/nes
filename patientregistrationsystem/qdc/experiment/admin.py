from django.contrib import admin
from experiment.models import Experiment, QuestionnaireResponse, StimulusType, FileFormat
from simple_history.admin import SimpleHistoryAdmin
from modeltranslation.admin import TranslationAdmin

admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)


class StimulusTypeAdmin(TranslationAdmin):
    pass


admin.site.register(StimulusType, StimulusTypeAdmin)
admin.site.register(FileFormat)
