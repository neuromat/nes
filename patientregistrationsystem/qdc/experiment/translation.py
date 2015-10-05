from modeltranslation.translator import translator, TranslationOptions
from experiment.models import StimulusType


class StimulusTypeTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(StimulusType, StimulusTypeTranslationOptions)
