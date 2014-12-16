from django.contrib import admin
from experiment.models import TimeUnit, Experiment, QuestionnaireConfiguration, QuestionnaireResponse
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(TimeUnit)
admin.site.register(StimulusType)
admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireConfiguration, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)
