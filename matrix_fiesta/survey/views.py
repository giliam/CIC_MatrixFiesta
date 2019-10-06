import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView

from common import auths
from matrix.models import ProfileUser
from survey import forms, models

class SurveyListView(ListView):
    model = models.Survey
    template_name = "survey/list.html"

    def get_queryset(self):
        return models.Survey.objects.filter(opened=True)
    

@login_required
@user_passes_test(auths.check_is_student)
def detail_survey(request, survey):
    survey = get_object_or_404(models.Survey, id=survey)
    response = models.Response.objects.filter(user__user=request.user)
    
    # If already answered, show answer.
    if len(response) >= 1 and len(response.filter(sent=True).all()) >= 1:
        print("Show answer")
        return render(request, "survey/answer.html", {"survey": survey, "response": response})
    elif len(response) >= 1:
        print("Edit answer")
        return render(request, "survey/answer.html", {"survey": survey})
    else:
        print("Show form and answer")
        return answer_survey(request, survey.id)


def answer_survey(request, survey):
    survey = get_object_or_404(models.Survey.objects.prefetch_related('questions', 'questions__choices'), id=survey)
    questions = survey.questions.all()
    if request.method == "POST":
        form = forms.ResponseForm(questions, request.POST)
        if form.is_valid():
            response = models.Response()
            response.survey = survey
            response.user = ProfileUser.objects.get(user=request.user)
            response.sent = True
            response.save()
            for question in questions.all():
                raw_answer = form.cleaned_data.get("question_"+str(question.id), None)
                if raw_answer:
                    answer = models.Answer()
                    answer.response = response
                    answer.question = question
                    answer.value = json.dumps(raw_answer)
                    answer.save()
            return redirect(reverse('survey.list'))

    else:
        form = forms.ResponseForm(questions)
    
    return render(request, 'survey/detail.html', {"survey": survey, "form": form})