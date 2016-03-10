# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from os.path import join
from update_english_data import translate_fixtures_into_english, update_translated_data


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):
    filename = join(settings.BASE_DIR, join("patient", join("fixtures", "load_initial_data.json")))

    fixtures_formatted_data = translate_fixtures_into_english(filename)
    update_translated_data(fixtures_formatted_data)


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0005_auto_20160304_1942'),
        ('experiment', '0002_auto_20151005_1521'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
