from django.core.management.base import BaseCommand, CommandError
from patient.models import ClassificationOfDiseases
from django.utils.translation.trans_real import activate, deactivate
from xml.etree import ElementTree


def format_text_element(label_element):
    formatted_text = ""
    if label_element.text:
        formatted_text = label_element.text

    term_elements = label_element.findall("Term")
    for term in term_elements:
        formatted_text += term.text
        if term.tail:
            formatted_text += term.tail

    return formatted_text


def icd_english_translation(tree):
    activate("en")

    codes = []
    icd_list = {}

    categories = tree.findall(".//Class/[@kind='category']")
    for category in categories:
        code = category.attrib['code']
        code = code.replace(".", "")

        label_element = category.find("Rubric[@kind='preferred']").find("Label")

        abbreviated_description = format_text_element(label_element)

        long_description = category.find("Rubric[@kind='preferredLong']")

        if long_description is not None:
            description = format_text_element(long_description.find("Label"))
        else:
            description = abbreviated_description

        icd_list[code] = [abbreviated_description, description]
        codes.append(code)

    classifications_of_diseases = ClassificationOfDiseases.objects.filter(code__in=codes)

    records_updated = 0

    for classification_of_disease in classifications_of_diseases:

        classification_of_disease.abbreviated_description = icd_list[classification_of_disease.code][0]
        classification_of_disease.description = icd_list[classification_of_disease.code][1]
        classification_of_disease.save()
        records_updated += 1

    deactivate()

    return records_updated


def import_classification_of_diseases(file_name):
    with open(file_name, 'rt') as f:
        tree = ElementTree.parse(f)

    return icd_english_translation(tree)


class Command(BaseCommand):
    help = 'Import ICD for translation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--en', nargs='?', type=str, help='english filename'
        )

    def handle(self, *args, **options):

        if options['en']:
            filename_english = options['en']
            try:
                import_classification_of_diseases(filename_english)
            except IOError:
                raise CommandError(
                    'Filename "%s" does not exist.' % filename_english
                )
            except UnicodeDecodeError:
                raise CommandError(
                    'Filename "%s" has incorrect format.' % filename_english
                )
            except ElementTree.ParseError:
                raise CommandError(
                    'Filename "%s" has incorrect format.' % filename_english
                )
