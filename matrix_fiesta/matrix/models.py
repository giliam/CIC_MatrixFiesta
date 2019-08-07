from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class DatedModel(models.Model):
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class Utilisateur(DatedModel):
    prenom = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s %s" % (self.prenom, self.nom.upper())


class Annee(DatedModel):
    nom = models.CharField(max_length=150)
    ordre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.nom.upper())

    class Meta:
        ordering = ['ordre']


class Semestre(DatedModel):
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


class UE(DatedModel):
    nom = models.CharField(max_length=150)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, related_name="ues", null=True)

    def __str__(self):
        return "%s (%s)" % (self.nom.upper(), self.semestre)

    class Meta:
        ordering = ['semestre']


class ECUE(DatedModel):
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


class Valeur(DatedModel):
    valeur = models.CharField(max_length=10)
    ordre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.valeur)

    class Meta:
        ordering = ["ordre"]


class AcquisApprentissage(DatedModel):
    nom = models.CharField(max_length=150)
    ecue = models.ForeignKey(ECUE, on_delete=models.SET_NULL, related_name="acquis", null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return "%s : %s" % (self.ecue, self.nom)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nom)
        super(AcquisApprentissage, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ["ecue", "nom"]


class EvaluationEleve(DatedModel):
    acquis = models.ForeignKey(AcquisApprentissage, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    valeur = models.ForeignKey(Valeur, on_delete=models.SET_NULL, null=True)
    evaluation_enseignant = models.BooleanField(default=False)

    def __str__(self):
        return "%s, %s : %s" % (self.acquis, self.eleve, self.valeur)

    class Meta:
        ordering = ["-added_date"]


class PetiteClasse(DatedModel):
    enseignant = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, 
        related_name="petites_classes_enseignant", null=True,
        limit_choices_to={'user__groups__name': 'Enseignants'}
    )
    ecue = models.ForeignKey(ECUE, on_delete=models.CASCADE, related_name="petites_classes")
    eleves = models.ManyToManyField(Utilisateur, related_name="petites_classes_eleve",
        limit_choices_to={'user__groups__name': 'Élèves'})

    def __str__(self):
        return "PC de %s par %s (%d élèves)" % (self.ecue, self.enseignant, self.eleves.count())