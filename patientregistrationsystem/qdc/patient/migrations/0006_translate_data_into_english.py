# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from django.db import migrations
from django.conf import settings

from update_english_data import translate_fixtures_into_english, update_translated_data

migration_commands_table = [
   "UPDATE patient_alcoholfrequency set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_alcoholperiod set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_amountcigarettes set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_fleshtone set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_gender set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_maritalstatus set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_payment set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_religion set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE patient_schooling set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
]


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):
    filename = join(settings.BASE_DIR, join("patient", join("fixtures", "load_initial_data_translation.json")))

    fixtures_formatted_data = translate_fixtures_into_english(filename)
    update_translated_data(fixtures_formatted_data)


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0005_auto_20160304_1942'),
        ('experiment', '0002_auto_20151005_1521'),
    ]

    operations = [
        migrations.RunSQL(migration_commands_table, ""),
        migrations.RunPython(load_data, backwards_data)
    ]
