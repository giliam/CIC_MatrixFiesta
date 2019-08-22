# Generated by Django 2.2.3 on 2019-08-22 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0009_auto_20190821_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=150)),
                ('value', models.PositiveIntegerField(default=0)),
                ('current', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Promotion year',
                'ordering': ['value'],
            },
        ),
        migrations.AlterModelOptions(
            name='evaluationvalue',
            options={'ordering': ['order'], 'verbose_name': 'Evaluation value'},
        ),
        migrations.AlterModelOptions(
            name='learningachievement',
            options={'ordering': ['course', 'name'], 'verbose_name': 'Learning achievement'},
        ),
        migrations.AlterModelOptions(
            name='profileuser',
            options={'verbose_name': 'User'},
        ),
        migrations.AlterModelOptions(
            name='schoolyear',
            options={'ordering': ['order'], 'verbose_name': 'School year'},
        ),
        migrations.AlterModelOptions(
            name='smallclass',
            options={'ordering': ['course'], 'verbose_name': 'Small class'},
        ),
        migrations.AlterModelOptions(
            name='studentevaluation',
            options={'ordering': ['-added_date'], 'verbose_name': 'Student evaluation'},
        ),
        migrations.RemoveField(
            model_name='profileuser',
            name='year_entrance',
        ),
        migrations.AddField(
            model_name='profileuser',
            name='year_entrance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='matrix.PromotionYear'),
        ),
        migrations.AddField(
            model_name='smallclass',
            name='promotion_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='small_classes', to='matrix.PromotionYear'),
        ),
    ]