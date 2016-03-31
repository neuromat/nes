from modeltranslation.translator import translator, TranslationOptions
from experiment.models import StimulusType, FileFormat


class StimulusTypeTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(StimulusType, StimulusTypeTranslationOptions)
