from django import forms
from django.contrib.auth.models import Group

from matrix import models

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur (email)", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class StudentEvaluationAllForm(forms.Form):
    # Based on https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.achievements_fields = []
        self.values = models.EvaluationValue.objects.all()
        self.choices = [(value.id, value.value) for value in self.values]
        self.worst_value = self.choices[0]

    def add_achievement_evaluation(self, achievement, default_value=None):      
        # Adds the field to the list of existing achievements related fields
        self.achievements_fields.append("achievement_"+str(achievement.id))

        self.fields["achievement_"+str(achievement.id)] = forms.ChoiceField(
            label=achievement.name,
            widget=forms.RadioSelect, choices=self.choices
        )
        if not default_value is None:
            self.initial["achievement_"+str(achievement.id)] = (default_value.id, default_value.value)
        else:
            self.initial["achievement_"+str(achievement.id)] = self.worst_value

    def get_cleaned_data(self, achievement):
        if "achievement_"+str(achievement.id) in self.cleaned_data.keys():
            return self.values.get(id=self.cleaned_data["achievement_"+str(achievement.id)])
        else:
            raise KeyError

class StudentEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.StudentEvaluation
        fields = ('evaluation_value',)

class TeacherEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.StudentEvaluation
        fields = ('evaluation_value','student',)


class UploadNewStudentsForm(forms.Form):
    has_header = forms.BooleanField(label="File has a header ?", required=False)
    file = forms.FileField(label='Select a file')
    group = forms.MultipleChoiceField(choices=[(g.id, g) for g in Group.objects.all() if g.name != "DE"])