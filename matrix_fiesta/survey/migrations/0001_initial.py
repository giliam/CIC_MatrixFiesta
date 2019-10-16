# Generated by Django 2.2.4 on 2019-10-06 18:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import survey.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('matrix', '0009_auto_20190924_0832'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=150)),
                ('opened', models.BooleanField(default=False)),
                ('slug', models.SlugField(unique=True)),
                ('ecue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='matrix.ECUE')),
            ],
            options={
                'verbose_name': 'Survey',
                'verbose_name_plural': 'Surveys',
                'ordering': ['ecue', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='survey.Survey')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Response',
                'verbose_name_plural': 'Responses',
                'ordering': ['survey', 'user'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.PositiveIntegerField(choices=[(0, survey.models.QuestionTypes(0)), (1, survey.models.QuestionTypes(1)), (2, survey.models.QuestionTypes(2)), (3, survey.models.QuestionTypes(3)), (4, survey.models.QuestionTypes(4)), (5, survey.models.QuestionTypes(5))], default=survey.models.QuestionTypes(0))),
                ('content', models.TextField()),
                ('required', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='survey.Survey')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
                'ordering': ['survey', 'content'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('value', models.TextField()),
                ('nb_elements', models.PositiveIntegerField(default=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Question')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='survey.Response')),
            ],
            options={
                'verbose_name': 'Answer',
                'verbose_name_plural': 'Answers',
                'ordering': ['question'],
            },
        ),
    ]