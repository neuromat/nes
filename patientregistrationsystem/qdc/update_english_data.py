import json

from django.apps import apps
from django.conf import settings
from django.core import management

SUFFIX_EN = "_en"
SUFFIX_pt_BR = "_pt_BR"


def translate_fixtures_into_english(filename):
    """
    :param filename: fixture json file
    :return: example:
    {'experiment.stimulustype': {'name': {'Somatosensorial': 'Somatosensory', 'Portugues': 'English'}}}
    experiment.stimulustype - model name
    name - model field name
    'Portugues': 'English' - word in Portuguese and its translation in English
    """
    with open(filename, encoding="utf-8") as fixture_data:
        data_transformed = json.load(fixture_data)

        result = {}

        for element in data_transformed:
            if element["model"] not in result:
                result[element["model"]] = {}

            # field_name = ''
            for field in element["fields"].keys():
                if field in settings.MODELTRANSLATION_CUSTOM_FIELDS:
                    # print(field)
                    field_name = field

                    if element["fields"][field_name]:
                        field_data_portuguese = element["fields"][
                            field_name + SUFFIX_pt_BR
                        ]
                        if field_name not in result[element["model"]]:
                            result[element["model"]][field_name] = {}

                        result[element["model"]][field_name][
                            field_data_portuguese
                        ] = element["fields"][field_name + SUFFIX_EN]

    return result


def update_translated_data(data):
    # update data in _pt_BR
    # management.call_command('update_translation_fields', verbosity=0, interactive=False)

    for data_model, data_values in data.items():
        model_db = apps.get_model(data_model)
        records_db = model_db.objects.all()

        for record in records_db:
            # print(record, record.name)
            for attrib, values in data_values.items():
                attrib_value_record = getattr(record, attrib)
                # print(attrib,attrib_value_record)
                if attrib_value_record:
                    # update data in _en
                    attrib_english = attrib + SUFFIX_EN
                    if attrib_value_record in list(values.keys()):
                        value_english = values[attrib_value_record]
                    else:
                        value_english = "Please translate this"

                    setattr(record, attrib_english, value_english)
                    # print(attrib_english, value_english)

            # print(record.name_pt_BR, record.name_en)
            # print("---------------------------------")
            record.save()
