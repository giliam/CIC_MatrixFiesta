from django.urls import path, re_path

from survey import views

urlpatterns = [
    path('', views.SurveyListView.as_view(), name="survey.list"),
    path('de/', views.SurveyListDeView.as_view(), name="survey.list_de"),

    re_path(r'detail/(?P<survey>[0-9]+)/', views.detail_survey, name="survey.detail"),
    re_path(r'detail/de/(?P<survey>[0-9]+)/', views.de_detail_survey, name="survey.detail_de"),
]


