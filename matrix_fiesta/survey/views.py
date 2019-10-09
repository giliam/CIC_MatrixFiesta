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
    survey = get_object_or_404(models.Survey.objects.prefetch_related('questions'), id=survey)
    response = models.Response.objects.filter(user__user=request.user).prefetch_related('answers', 'answers__question')
    
    # If already answered, show answer.
    if len(response) >= 1 and len(response.filter(sent=True).all()) >= 1:
        response = response[0]
        response.prepare_answers_for_template(survey.questions.all())
        return render(request, "survey/answer.html", {"survey": survey, "response": response, "QuestionTypes": models.QuestionTypes})
    elif len(response) >= 1:
        response = response[0]
        return answer_survey(request, survey.id, response)
    else:
        return answer_survey(request, survey.id)


def answer_survey(request, survey, response=None):
    survey = get_object_or_404(models.Survey.objects.prefetch_related('questions', 'questions__choices'), id=survey)
    questions = survey.questions.all()
    if request.method == "POST":
        form = forms.ResponseForm(questions, request.POST)
        if form.is_valid():
            choices_by_question = {}
            choices_id = set()
            for question in questions.all():
                question_choices = [c.id for c in question.choices.all()]
                choices_id.update(question_choices)
                choices_by_question[question.id] = (question_choices)
            choices = models.QuestionChoice.objects.filter(id__in=choices_id)
            choices_by_id = {c.id: c for c in choices.all()}
            if response is None:
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
                    answer.save()
                    if question.is_iterable():
                        json_raw_answer = []
                        for elt in raw_answer:
                            id_elt = int(elt)
                            if id_elt in choices_by_question[question.id]:
                                answer.choices.add(choices_by_id[id_elt])
                                json_raw_answer.append(choices_by_id[id_elt].value)
                            else:
                                raise ValueError("Couldn't find elt", id_elt, "in choices available", choices_by_question[question.id])
                        answer.value = json.dumps(json_raw_answer)
                    else:
                        answer.value = json.dumps(raw_answer)
                    answer.save()
            return redirect(reverse('survey.list'))
    else:
        if response is None:
            form = forms.ResponseForm(questions)
        else:
            response.prepare_answers_for_form(questions)
            form = forms.ResponseForm(questions)
            form.set_initial(response)
    
    return render(request, 'survey/detail.html', {"survey": survey, "form": form})