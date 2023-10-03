from experiment.models import (
    AmplifierDetectionType,
    CoilShape,
    ElectrodeConfiguration,
    ElectrodeShape,
    FileFormat,
    SourceCodeFileFormat,
    InformationType,
    InformationTypeMedia,
    MeasureSystem,
    PublicationType,
    StimulusType,
    TetheringSystem,
)
from modeltranslation.translator import TranslationOptions, translator


class PublicationTypeTranslationOptions(PublicationType):
    fields = ("name",)


translator.register(PublicationType, TranslationOptions)


class StimulusTypeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(StimulusType, StimulusTypeTranslationOptions)


class FileFormatTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(FileFormat, FileFormatTranslationOptions)


class SourceCodeFileFormatTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(SourceCodeFileFormat, SourceCodeFileFormatTranslationOptions)


class ElectrodeShapeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(ElectrodeShape, ElectrodeShapeTranslationOptions)


class MeasureSystemTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(MeasureSystem, MeasureSystemTranslationOptions)


class TetheringSystemTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(TetheringSystem, TetheringSystemTranslationOptions)


class AmplifierDetectionTypeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(AmplifierDetectionType, AmplifierDetectionTypeTranslationOptions)


class ElectrodeConfigurationTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(ElectrodeConfiguration, ElectrodeConfigurationTranslationOptions)


class CoilShapeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(CoilShape, CoilShapeTranslationOptions)


class InformationTypeTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(InformationType, InformationTypeTranslationOptions)


class InformationTypeMediaTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(InformationTypeMedia, InformationTypeMediaTranslationOptions)
