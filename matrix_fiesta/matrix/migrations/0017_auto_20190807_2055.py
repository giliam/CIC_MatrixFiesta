# Generated by Django 2.2.4 on 2019-08-07 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0016_auto_20190807_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='petiteclasse',
            name='eleves',
            field=models.ManyToManyField(limit_choices_to={'user__groups__name': 'Élèves'}, related_name='petites_classes_eleve', to='matrix.Utilisateur'),
        ),
    ]
