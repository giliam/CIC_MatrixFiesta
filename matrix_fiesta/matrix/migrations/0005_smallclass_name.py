# Generated by Django 2.2.4 on 2019-09-02 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0004_profileuser_cas_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='smallclass',
            name='name',
            field=models.CharField(default='', max_length=150, null=True),
        ),
    ]