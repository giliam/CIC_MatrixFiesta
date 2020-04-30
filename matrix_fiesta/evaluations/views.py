import os

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.views.static import serve

from common import auths
from evaluations import models


@login_required
@user_passes_test(auths.check_is_student)
def list_evaluations(request):
    ev_results = models.EvaluationResult.objects.filter(
        user__user=request.user
    ).prefetch_related("evaluation")
    return render(request, "evaluations/list.html", {"results": ev_results})


@login_required
@user_passes_test(auths.check_is_student)
def download_result(request, ev_id):
    ev_result = get_object_or_404(
        models.EvaluationResult, Q(id=ev_id, user__user=request.user)
    )
    file_name = ev_result.filepath
    path_to_file = file_name
    # en mode debug, on demande à Django de servir le fichier histoire de pas
    # être forcé de setuper nginx sur sa machine de dev
    if settings.DEBUG:
        return serve(request, path_to_file, settings.SECURE_MEDIA_ROOT)

    # Sinon on retourne une réponse VIDE avec en header le chemin de l'url
    # de l'upload interne
    # Nginx va l'intercepter, réaliser qu'il faut qu'il upload ce qu'il y
    # a à cette URL et faire le reste du boulot
    response = HttpResponse()
    response["X-Accel-Redirect"] = "/supload/%s" % path_to_file
    return response
