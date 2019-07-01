from django import forms
from matrix.models import EvaluationEleve

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur (email)", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class EvaluationEleveForm(forms.ModelForm):
    class Meta:
        model = EvaluationEleve
        fields = ('valeur',)