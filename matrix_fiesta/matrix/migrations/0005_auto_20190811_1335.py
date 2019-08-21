# Generated by Django 2.2.3 on 2019-08-11 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matrix', '0004_studentevaluation_last_evaluation'),
    ]
    
    atomic = False

    operations = [
        migrations.RenameModel('ECUE', 'Course'),
        migrations.RenameField(
            model_name='learningachievement',
            old_name='ecue',
            new_name='course'
        ),
        migrations.RenameField(
            model_name='smallclass',
            old_name='ecue',
            new_name='course'
        ),
        migrations.AlterModelOptions(
            name='learningachievement',
            options={'ordering': ['course', 'name'], 'verbose_name': 'AcquisApprentissage'},
        ),
        migrations.AlterModelOptions(
            name='smallclass',
            options={'ordering': ['course'], 'verbose_name': 'PetiteClasse'},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['ue', 'name'], 'verbose_name': 'Course'},
        ),
        migrations.AlterField(
            model_name='course',
            name='ue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='matrix.UE'),
        ),
    ]
