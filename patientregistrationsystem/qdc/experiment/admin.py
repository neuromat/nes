from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ADConverter,
    AmplifierDetectionType,
    BrainArea,
    BrainAreaSystem,
    CoilOrientation,
    DirectionOfTheInducedCurrent,
    ElectrodeConfiguration,
    ElectrodeShape,
    FileFormat,
    GenericDataCollection,
    GoalkeeperGame,
    GoalkeeperPhase,
    InformationType,
    InformationTypeMedia,
    MeasureSystem,
    MeasureUnit,
    PublicationType,
    QuestionnaireResponse,
    SourceCodeFileFormat,
    StandardizationSystem,
    StimulusType,
    Tag,
    TetheringSystem,
)

admin.site.register(QuestionnaireResponse, SimpleHistoryAdmin)


class StimulusTypeAdmin(TranslationAdmin):
    pass


admin.site.register(StimulusType, StimulusTypeAdmin)
admin.site.register(Tag)

admin.site.register(ElectrodeShape)
admin.site.register(MeasureSystem)
admin.site.register(MeasureUnit)
admin.site.register(TetheringSystem)
admin.site.register(AmplifierDetectionType)
admin.site.register(ElectrodeConfiguration)
admin.site.register(ADConverter)
admin.site.register(StandardizationSystem)
admin.site.register(CoilOrientation)
admin.site.register(DirectionOfTheInducedCurrent)
admin.site.register(BrainArea)
admin.site.register(BrainAreaSystem)
admin.site.register(InformationType)
admin.site.register(InformationTypeMedia)
admin.site.register(FileFormat)
admin.site.register(SourceCodeFileFormat)
admin.site.register(PublicationType)
admin.site.register(GoalkeeperGame)
admin.site.register(GoalkeeperPhase)
