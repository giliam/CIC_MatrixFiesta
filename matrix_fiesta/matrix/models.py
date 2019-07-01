from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.

class Utilisateur(models.Model):
    prenom = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s %s" % (self.prenom, self.nom.upper())


class Annee(models.Model):
    nom = models.CharField(max_length=150)
    ordre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.nom.upper())

    class Meta:
        ordering = ['ordre']


class Semestre(models.Model):
    nom = models.CharField(max_length=150)
    ordre = models.PositiveIntegerField(default=0)
    annee = models.ForeignKey(
        Annee, 
        on_delete=models.SET_NULL, null=True,
        related_name="semestres"
    )

    def __str__(self):
        return "%s" % (self.nom.upper())

    class Meta:
        ordering = ['ordre']


class UE(models.Model):
    nom = models.CharField(max_length=150)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, related_name="ues", null=True)

    def __str__(self):
        return "%s (%s)" % (self.nom.upper(), self.semestre)

    class Meta:
        ordering = ['semestre']


class ECUE(models.Model):
    nom = models.CharField(max_length=150)
    ue = models.ForeignKey(UE, on_delete=models.SET_NULL, related_name="ecues", null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return "%s - %s" % (self.nom.upper(), self.ue)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nom)
        super(ECUE, self).save(*args, **kwargs)

    class Meta:
        ordering = ['ue', 'nom']


class EchelleValeurs(models.Model):
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    type_echelle = models.CharField(max_length=100, choices=[
            ("1", "Entiers"), 
            ("2", "Valeurs")
    ])

    def __str__(self):
        return "%s (%s)" % (self.nom, self.type_echelle)


class Valeur(models.Model):
    valeur = models.CharField(max_length=10)
    echelle = models.ForeignKey(EchelleValeurs, on_delete=models.CASCADE)
    ordre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.valeur)

    class Meta:
        ordering = ["echelle", "ordre"]


class AcquisApprentissage(models.Model):
    nom = models.CharField(max_length=150)
    ecue = models.ForeignKey(ECUE, on_delete=models.SET_NULL, related_name="acquis", null=True)
    valeurs = models.ForeignKey(EchelleValeurs, on_delete=models.SET_NULL, related_name="+", null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return "%s : %s" % (self.ecue, self.nom)

    class Meta:
        ordering = ["ecue", "nom"]        


class EvaluationEleve(models.Model):
    acquis = models.ForeignKey(AcquisApprentissage, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    valeur = models.ForeignKey(Valeur, on_delete=models.SET_NULL, null=True)
    evaluation_enseignant = models.BooleanField(default=False)