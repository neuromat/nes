from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from patient.models import ClassificationOfDiseases
from django.utils.translation.trans_real import activate, deactivate

import csv
import os

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):

        filename = 'icd10cid10v2017.csv'
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

    path = settings.BASE_DIR
    os.chdir(path)
    os.chdir(os.path.join('..', '..','resources', 'load-idc-table'))

    # varify the path using getcwd()
    # cwd = os.getcwd()
    # print("Current working directory is:", cwd)

    with open(file_name, 'r') as csvFile:
        reader = csv.reader(csvFile)
        next(reader, None)
        for row in reader:
            # print(row[0]) # Codigo
            # print(row[1]) # Ingles longo
            # print(row[2]) # Portugues longo
            # print(row[3]) # Portugues curto

            classifications_of_diseases = ClassificationOfDiseases.objects.create(
                code=row[0], description=row[2], abbreviated_description=row[3]
            )

            # colunas _en
            activate("en")
            classifications_of_diseases.description = row[1]
            classifications_of_diseases.abbreviated_description = row[1]
            classifications_of_diseases.save()
            deactivate()



