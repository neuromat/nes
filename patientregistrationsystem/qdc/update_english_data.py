import json
from django.conf import settings
from django.apps import apps

suffix_en = "_en"
suffix_pt_br = "_pt_br"


def translate_fixtures_into_english(filename):
    json_data = open(filename)

    data = json.load(json_data)

    result = {}

    for info in data:
        if info['model'] not in result:
            result[info['model']] = {}

        field_name = ''
        for field in info['fields'].keys():
            if field in settings.MODELTRANSLATION_CUSTOM_FIELDS:
                field_name = field
                break

        field_name_portuguese = field_name + suffix_pt_br
        field_data_portuguese = info['fields'][field_name_portuguese]
        if field_name_portuguese not in result[info['model']]:
            result[info['model']][field_name_portuguese] = {}

        result[info['model']][field_name_portuguese][field_data_portuguese] = info['fields'][field_name + suffix_en]

    return result


def update_translated_data(data):

    for data_model, data_values in data.items():

        model_db = apps.get_model(data_model)
        records_db = model_db.objects.all()
        for record in records_db:
            # print(record, record.name)
            for attrib, values in data_values.items():
                attrib_value = getattr(record, attrib)
                attrib_english = attrib.replace(suffix_pt_br, suffix_en)
                if attrib_value in list(values.keys()):
                    value_english = values[attrib_value]
                else:
                    value_english = "Please translate this"
                setattr(record, attrib_english, value_english)
            print(record.name_pt_br, record.name_en)
            print("---------------------------------")
            record.save()