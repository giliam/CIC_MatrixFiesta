# Generated by Django 2.2.4 on 2019-10-06 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=150)),
            ],
            options={
                'ordering': ['value'],
            },
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['survey', 'order'], 'verbose_name': 'Question', 'verbose_name_plural': 'Questions'},
        ),
        migrations.AddField(
            model_name='response',
            name='sent',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='response',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='matrix.ProfileUser'),
        ),
        migrations.AddField(
            model_name='question',
            name='choices',
            field=models.ManyToManyField(to='survey.QuestionChoice'),
        ),
    ]
