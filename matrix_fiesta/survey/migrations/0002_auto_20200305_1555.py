# Generated by Django 2.2.10 on 2020-03-05 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="response",
            options={
                "ordering": ["survey", "updated_date", "added_date"],
                "verbose_name": "Response",
                "verbose_name_plural": "Responses",
            },
        ),
    ]
