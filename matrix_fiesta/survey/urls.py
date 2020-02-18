from django.urls import path, re_path

from survey import views

urlpatterns = [
    path("", views.SurveyListView.as_view(), name="survey.list"),
    path("de/", views.SurveyListDeView.as_view(), name="survey.list_de"),
    path("de/creation/", views.create_survey_de, name="survey.create_survey_de"),
    re_path(r"detail/(?P<survey>[0-9]+)/", views.detail_survey, name="survey.detail"),
    re_path(
        r"de/results/(?P<survey>[0-9]+)/",
        views.de_results_survey,
        name="survey.results_de",
    ),
    re_path(
        r"de/edit/(?P<survey>[0-9]+)/", views.de_edit_survey, name="survey.edit_de"
    ),
    re_path(
        r"de/clear/(?P<survey>[0-9]+)/", views.de_clear_survey, name="survey.clear_de"
    ),
    re_path(
        r"de/edit/add/question/(?P<survey>[0-9]+)/",
        views.de_add_question,
        name="survey.add_question_de",
    ),
    re_path(
        r"de/edit/move/question/(?P<question>[0-9]+)/(?P<direction>up|down)",
        views.de_move_question,
        name="survey.move_question_de",
    ),
    re_path(
        r"de/edit/remove/question/(?P<question>[0-9]+)/",
        views.de_remove_question,
        name="survey.remove_question_de",
    ),
    re_path(
        r"de/edit/question/(?P<question>[0-9]+)/",
        views.de_edit_question,
        name="survey.edit_question_de",
    ),
]
