# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from os.path import join

from django.db import migrations
from django.conf import settings
from update_english_data import translate_fixtures_into_english, update_translated_data

migration_commands_table = [
   "UPDATE experiment_fileformat set name_pt_br = name WHERE name <> '' and (name_pt_br = '' or name_pt_br is null);",
   "UPDATE experiment_fileformat set description_pt_br = description WHERE description <> '' and (description_pt_br = '' or description_pt_br is null);",
]


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    # update_translation_fields

    filename = join(settings.BASE_DIR, join("experiment", join("fixtures", "load_initial_data_translation.json")))

    fixtures_formatted_data = translate_fixtures_into_english(filename)

    update_translated_data(fixtures_formatted_data)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0015_auto_20160512_2026'),
    ]

    operations = [
        migrations.RunSQL(migration_commands_table, ""),
        migrations.RunPython(load_data, backwards_data),
    ]
