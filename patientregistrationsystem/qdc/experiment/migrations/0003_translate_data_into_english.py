# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from django.db import migrations
from django.conf import settings
from update_english_data import translate_fixtures_into_english, update_translated_data


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    # update_translation_fields

    filename = join(settings.BASE_DIR, join("experiment", join("fixtures", "load_initial_data_translation.json")))

    fixtures_formatted_data = translate_fixtures_into_english(filename)
    update_translated_data(fixtures_formatted_data)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0002_auto_20151005_1521'),
        ('patient', '0006_translate_data_into_english'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
