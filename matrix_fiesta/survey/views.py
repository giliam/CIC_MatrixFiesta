from django.shortcuts import render
from django.views.generic import ListView

from survey.models import Survey

class SurveyListView(ListView):
    model = Survey
    template_name = "survey/list.html"
