from django.contrib import admin
from experiment.models import Experiment, QuestionnaireConfiguration, QuestionnaireResponse, StimulusType
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(StimulusType)
admin.site.register(Experiment, SimpleHistoryAdmin)
admin.site.register(QuestionnaireConfiguration, SimpleHistoryAdmin)
admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)
