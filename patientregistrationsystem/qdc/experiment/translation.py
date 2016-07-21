from modeltranslation.translator import translator, TranslationOptions
from experiment.models import StimulusType, FileFormat, \
    ElectrodeShape, MeasureSystem, TetheringSystem, AmplifierDetectionType, ElectrodeConfiguration


class StimulusTypeTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(StimulusType, StimulusTypeTranslationOptions)


class FileFormatTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

translator.register(FileFormat, FileFormatTranslationOptions)


class ElectrodeShapeTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(ElectrodeShape, ElectrodeShapeTranslationOptions)


class MeasureSystemTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(MeasureSystem, MeasureSystemTranslationOptions)


class TetheringSystemTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(TetheringSystem, TetheringSystemTranslationOptions)


class AmplifierDetectionTypeTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(AmplifierDetectionType, AmplifierDetectionTypeTranslationOptions)


class ElectrodeConfigurationTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(ElectrodeConfiguration, ElectrodeConfigurationTranslationOptions)
