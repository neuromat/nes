# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import Group


GroupTableTranslate = {
 "Administrador": "Administrator",
 "Atendente":  "Attendant",
 "Fisioterapeuta": "Physiotherapist",
 "Médico": "Doctor",
 "Pesquisador júnior": "Junior researcher",
 "Pesquisador sênior": "Senior researcher",
}


def backwards_data(apps, schema_editor):
    print("backwards data")


def update_goup_data(apps, schema_editor):

    groups = Group.objects.all()
    for group in groups:
        if group.name in list(GroupTableTranslate.keys()):
            group.name = GroupTableTranslate[group.name]
            group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0002_auto_20151006_1451'),
    ]

    operations = [
        migrations.RunPython(update_goup_data, backwards_data)
    ]
