# Generated by Django 4.1.10 on 2023-08-13 00:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("plugin", "0005_randomforests_followup_assessment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="randomforests",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
