from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from patient.models import ClassificationOfDiseases
from django.utils.translation.trans_real import activate, deactivate

import csv
import os

class Command(BaseCommand):
    help = 'Import ICD for translation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', nargs='?', type=str, help='codes filename'
        )
    def handle(self, *args, **options):
        # filename = 'icd10cid10v2017.csv'
        if options['file']:
            filename = options['file']
            try:
                import_classification_of_icd_cid(filename)
            except IOError:
                raise CommandError(
                'Filename "%s" does not exist.' % filename
                )
            except UnicodeDecodeError:
                raise CommandError(
                'Filename "%s" has incorrect format.' % filename
                )


def import_classification_of_icd_cid(file_name):
    # path = settings.BASE_DIR
    # os.chdir(path)
    # os.chdir(os.path.join('..', '..','resources', 'load-idc-table'))
    filename = os.path.join(settings.BASE_DIR,
                            os.path.join("..", "..", os.path.join("resources", "load-idc-table", file_name)))

    with open(filename, 'r') as csvFile:
        reader = csv.reader(csvFile)
        next(reader, None)
        for row in reader:

            classifications_of_diseases = ClassificationOfDiseases.objects.create(
                code=row[0], description=row[2], abbreviated_description=row[3]
            )

            # colunas _en
            activate("en")
            classifications_of_diseases.description = row[1]
            classifications_of_diseases.abbreviated_description = row[1]
            classifications_of_diseases.save()
            deactivate()



