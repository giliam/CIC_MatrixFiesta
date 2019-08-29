from django import forms
from django.contrib.auth import models as auth_models
from django.utils.translation import gettext as _

from matrix import models
from common.auths import GroupsNames

class ConnexionForm(forms.Form):
    username = forms.CharField(label=_("User name"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

class StudentEvaluationAllForm(forms.Form):
    # Based on https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.achievements_fields = []
        self.values = models.EvaluationValue.objects.all()
        self.choices = [(0, 0)] + [(value.id, value.value) for value in self.values]
        self.worst_value = self.choices[0]

    def add_achievement_evaluation(self, achievement, default_value=None):      
        # Adds the field to the list of existing achievements related fields
        self.achievements_fields.append("achievement_"+str(achievement.id))

        self.fields["achievement_"+str(achievement.id)] = forms.ChoiceField(
            label=achievement.name,
            widget=forms.RadioSelect, choices=self.choices,
            required=False
        )
        if not default_value is None:
            self.initial["achievement_"+str(achievement.id)] = (default_value.id, default_value.value)
        else:
            self.initial["achievement_"+str(achievement.id)] = self.worst_value

    def get_cleaned_data(self, achievement):
        if "achievement_"+str(achievement.id) in self.cleaned_data.keys():
            id_value = self.cleaned_data["achievement_"+str(achievement.id)]
            if id_value == '0' or id_value == '':
                return None
            else:
                return self.values.get(id=id_value)
        else:
            raise KeyError

class StudentEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.StudentEvaluation
        fields = ('evaluation_value',)
        labels = {
            "evaluation_value": _("Evaluation value"),
        }

class TeacherEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.StudentEvaluation
        fields = ('evaluation_value','student',)
        labels = {
            "evaluation_value": _("Evaluation value"),
            "student": _("Student")
        }


def get_groups():
    try: 
        return [(g.id, g) for g in auth_models.Group.objects.all() if g.name != GroupsNames.DIRECTOR_LEVEL.value]
    except:
        return []

class UploadNewStudentsForm(forms.Form):
    has_header = forms.BooleanField(label=_("File has a header ?"), required=False)
    file = forms.FileField(label=_('Select a file'))
    group = forms.MultipleChoiceField(choices=get_groups)
