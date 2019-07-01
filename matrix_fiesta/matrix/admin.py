from django.contrib import admin

from matrix import models


admin.site.register(models.Utilisateur)
admin.site.register(models.Annee)
admin.site.register(models.Semestre)
admin.site.register(models.UE)
admin.site.register(models.ECUE)
admin.site.register(models.AcquisApprentissage)
