from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse
from django.views.decorators.debug import sensitive_post_parameters

from matrix import forms
from matrix import models

def homepage(request):
    return render(request, "homepage.html")


@login_required
def liste_ues(request):
    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre')
    return render(request, "matrix/liste_ues.html", {"ues":ues})


@login_required
def matrix_ecue(request, slug):
    ecue = models.ECUE.objects.get(slug=slug)
    utilisateur = models.Utilisateur.objects.get(user=request.user)
    acquis = models.AcquisApprentissage.objects.filter(ecue=ecue)
    evaluations = models.EvaluationEleve.objects.filter(
        eleve=utilisateur, 
        evaluation_enseignant=False
    ).prefetch_related('acquis', 'valeur')

    evaluations_acquis = {}

    for evaluation in evaluations.all():
        if evaluation.acquis.id in evaluations_acquis.keys():
            evaluations_acquis[evaluation.acquis.id]["history"].append({
                "value": evaluation.valeur, "date": evaluation.added_date
            })
            continue
        evaluations_acquis[evaluation.acquis.id] = {
            "last": {
                "value": evaluation.valeur, "date": evaluation.added_date
            },
            "history": []
        }

    return render(request, "matrix/matrix_ecue.html", {
        "ecue":ecue, "acquis":acquis, "evaluations":evaluations, "evaluations_acquis":evaluations_acquis
    })


@sensitive_post_parameters('password')
def connexion(request):
    error = False
    if request.method == "POST":
        form = forms.ConnexionForm(request.POST)
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
        form = forms.ConnexionForm()
    return render(request, 'users/login.html',locals())


@login_required
def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))


@login_required
def evaluer_acquis(request, slug):
    acquis = models.AcquisApprentissage.objects.get(slug=slug)

    eleve = models.Utilisateur.objects.get(user=request.user)
    try:
        evaluation_existante = models.EvaluationEleve.objects.get(acquis=acquis, eleve=eleve, evaluation_enseignant=False)
        # return redirect('ues.matrix_ecue', acquis.ecue.slug)
    except models.EvaluationEleve.DoesNotExist:
        pass
    except models.EvaluationEleve.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.EvaluationEleveForm(request.POST)
        if form.is_valid():
            evaluation_eleve = form.save(commit=False)
            evaluation_eleve.acquis = acquis
            evaluation_eleve.eleve = eleve
            evaluation_eleve.evaluation_enseignant = False
            evaluation_eleve.save()
            return redirect('ues.matrix_ecue', acquis.ecue.slug)
    else:
        form = forms.EvaluationEleveForm()
    return render(request, "matrix/evaluer_acquis.html", {"form":form, "acquis": acquis})