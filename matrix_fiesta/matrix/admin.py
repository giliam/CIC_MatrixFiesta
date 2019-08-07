from django.contrib import admin

from matrix import models

class SlugNameAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}



admin.site.register(models.ProfileUser)
admin.site.register(models.SchoolYear)
admin.site.register(models.Semestre)
admin.site.register(models.UE)
admin.site.register(models.ECUE, SlugNameAdmin)
admin.site.register(models.EvaluationValue)
admin.site.register(models.LearningAchievement, SlugNameAdmin)
admin.site.register(models.StudentEvaluation)
admin.site.register(models.SmallClass)
