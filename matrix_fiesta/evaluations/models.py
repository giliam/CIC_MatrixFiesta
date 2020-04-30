from django.db import models
from django.utils.translation import ugettext_lazy as _

from matrix.models import DatedModel, ProfileUser


class FinalEvaluation(DatedModel):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return _("Final evaluation %(name)s") % {"name": self.name}

    class Meta:
        verbose_name = _("Final evaluation")
        verbose_name_plural = _("Final evaluations")
        ordering = ["updated_date", "added_date"]


class EvaluationResult(DatedModel):
    user = models.ForeignKey(ProfileUser, null=False, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(
        FinalEvaluation, null=False, on_delete=models.CASCADE
    )
    filepath = models.CharField(max_length=500, null=False)
    downloaded = models.BooleanField(default=False)

    def __str__(self):
        return _("Evaluation result for %(user)s") % {"user": self.user}

    class Meta:
        verbose_name = _("Evaluation result")
        verbose_name_plural = _("Evaluation results")
        ordering = ["evaluation", "user", "updated_date", "added_date"]
