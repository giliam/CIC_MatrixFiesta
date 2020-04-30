from django.urls import path, re_path

from evaluations import views

urlpatterns = [
    path("", views.list_evaluations, name="evaluations.list"),
    re_path(
        r"download/(?P<ev_id>[0-9]+)/",
        views.download_result,
        name="evaluations.download",
    ),
]
