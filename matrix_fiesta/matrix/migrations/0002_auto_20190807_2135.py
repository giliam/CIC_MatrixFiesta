# Generated by Django 2.2.4 on 2019-08-07 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learningachievement',
            name='ecue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='achievements', to='matrix.ECUE'),
        ),
    ]