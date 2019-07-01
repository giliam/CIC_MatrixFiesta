from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse
from django.views.decorators.debug import sensitive_post_parameters

from matrix.forms import ConnexionForm
from matrix import models

def homepage(request):
    return render(request, "homepage.html")


def liste_ues(request):
    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre')
    return render(request, "matrix/liste_ues.html", {"ues":ues})


def matrix_ecue(request, slug):
    ecue = models.ECUE.objects.get(slug=slug)
    return render(request, "matrix/matrix_ecue.html", {"ecue":ecue})


@sensitive_post_parameters('password')
def connexion(request):
    error = False
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"] # Nous récupérons le nom d'utilisateur
            password = form.cleaned_data["password"] # … et le mot de passe
            user = authenticate(username=username, password=password) #Nous vérifions si les données sont correctes
            if user: # Si l'objet renvoyé n'est pas None
                login(request, user) # nous connectons l'utilisateur
                return redirect("homepage")
            else: #sinon une erreur sera affichée
                error = True
    else:
        form = ConnexionForm()
    return render(request, 'users/login.html',locals())


def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))
