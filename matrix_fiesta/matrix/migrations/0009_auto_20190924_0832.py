# Generated by Django 2.2.5 on 2019-09-24 06:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0008_auto_20190912_1453'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profileuser',
            options={'ordering': ['user__last_name', 'user__first_name'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
