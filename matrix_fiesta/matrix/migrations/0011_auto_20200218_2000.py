# Generated by Django 2.2.4 on 2020-02-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matrix", "0010_evaluationvalue_counts_for_average"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=models.SlugField(max_length=250, unique=True),
        ),
        migrations.AlterField(
            model_name="learningachievement",
            name="slug",
            field=models.SlugField(max_length=250, unique=True),
        ),
    ]
