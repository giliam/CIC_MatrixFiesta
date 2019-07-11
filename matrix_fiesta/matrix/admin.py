from django.contrib import admin

from matrix import models

class SlugNomAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nom",)}



admin.site.register(models.EchelleValeurs)
admin.site.register(models.EvaluationEleve)
admin.site.register(models.Valeur)
admin.site.register(models.Utilisateur)
admin.site.register(models.Annee)
admin.site.register(models.Semestre)
admin.site.register(models.UE)
admin.site.register(models.ECUE, SlugNomAdmin)
admin.site.register(models.AcquisApprentissage, SlugNomAdmin)
