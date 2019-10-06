from django.urls import path, re_path

from survey import views

urlpatterns = [
    path('', views.SurveyListView.as_view(), name="survey.list"),

    re_path(r'(?P<survey>[0-9]+)/', views.detail_survey, name="survey.detail"),
]


