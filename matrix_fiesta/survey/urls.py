from django.urls import path, re_path

from survey import views

urlpatterns = [
    path('', views.SurveyListView.as_view(), name="survey.list"),
]


