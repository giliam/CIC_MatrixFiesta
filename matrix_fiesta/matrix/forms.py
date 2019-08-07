from django import forms
from matrix.models import StudentEvaluation

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur (email)", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class StudentEvaluationForm(forms.ModelForm):
    class Meta:
        model = StudentEvaluation
        fields = ('evaluation_value',)

class TeacherEvaluationForm(forms.ModelForm):
    class Meta:
        model = StudentEvaluation
        fields = ('evaluation_value','student',)