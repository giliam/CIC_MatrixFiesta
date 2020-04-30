from django.contrib import admin

from evaluations import models

admin.site.register(models.FinalEvaluation)
admin.site.register(models.EvaluationResult)
