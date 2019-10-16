from itertools import chain
import json
from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from common import auths
from matrix.models import ProfileUser
from survey import forms, models


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(auths.check_is_student), name="dispatch")
class SurveyListView(ListView):
    model = models.Survey
    template_name = "survey/list.html"

    def get_queryset(self):
        # cf. https://stackoverflow.com/a/48910072/8980220
        profile_user = ProfileUser.objects.get(user=self.request.user)

        surveys = models.Survey.objects.filter(
            Q(opened=True),
            Q(promotionyear=profile_user.year_entrance) | Q(promotionyear=None)
        )
        responses = models.Response.objects.filter(
            user__user=self.request.user,
            survey__opened=False
        ).prefetch_related('survey')
        responses_live = models.Response.objects.filter(
            user__user=self.request.user,
            survey__opened=True
        ).prefetch_related('survey')
        responses_opened = {}
        for response in responses_live.all():
            responses_opened[response.survey.id] = response
        return {
            "surveys": surveys,
            "responses": responses,
            "responses_opened": responses_opened
        }


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(auths.check_is_de), name="dispatch")
class SurveyListDeView(ListView):
    model = models.Survey
    template_name = "survey/list_de.html"

    def get_queryset(self):
        surveys = models.Survey.objects.all().prefetch_related('responses')
        return {"surveys": surveys}


@login_required
@user_passes_test(auths.check_is_de)
def de_detail_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related('questions'),
        Q(id=survey)
    )
    responses = models.Response.objects.filter(survey=survey).prefetch_related(
        'answers', 'answers__question'
    )
    
    return render(request, "survey/detail_de.html", {"survey": survey})


@login_required
@user_passes_test(auths.check_is_student)
def detail_survey(request, survey):
    profile_user = ProfileUser.objects.get(user=request.user)
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related('questions'),
        Q(id=survey),
        Q(promotionyear=profile_user.year_entrance) | Q(promotionyear=None)
    )
    response = models.Response.objects.filter(
        survey=survey, user__user=request.user
    ).prefetch_related('answers', 'answers__question')
    
    # If already answered, show answer.
    if len(response) >= 1 and len(response.filter(sent=True).all()) >= 1:
        response = response[0]
        response.prepare_answers_for_template(survey.questions.all())
        return render(request, "survey/answer.html", {"survey": survey, "response": response, "QuestionTypes": models.QuestionTypes})
    elif len(response) >= 1:
        response = response[0]
        return answer_survey(request, survey.id, response)
    elif survey.opened:
        return answer_survey(request, survey.id)
    else:
        return redirect(reverse('survey.list'))


def answer_survey(request, survey, response=None):
    survey = get_object_or_404(models.Survey.objects.prefetch_related('questions', 'questions__choices'), id=survey)
    questions = survey.questions.all()
    if request.method == "POST":
        form = forms.ResponseForm(questions, request.POST, anonymous=survey.allow_anonymous)
        if form.is_valid():
            
            # reorganizes the choices by question
            choices_by_question = {}
            choices_id = set()
            for question in questions.all():
                question_choices = [c.id for c in question.choices.all()]
                choices_id.update(question_choices)
                choices_by_question[question.id] = (question_choices)
            choices = models.QuestionChoice.objects.filter(id__in=choices_id)
            choices_by_id = {c.id: c for c in choices.all()}
            
            # if this is not an edition, create a new response
            if response is None:
                response = models.Response()
            response.survey = survey
            response.anonymous = survey.allow_anonymous and form.cleaned_data["anonymous"]
            response.user = ProfileUser.objects.get(user=request.user)
            # checks whether it is a saving or submitting action
            response.sent = "submit" in request.POST and not "save" in request.POST
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
            form = forms.ResponseForm(questions, anonymous=survey.allow_anonymous)
        else:
            response.prepare_answers_for_form(questions)
            form = forms.ResponseForm(questions, anonymous=survey.allow_anonymous)
            form.set_initial(response)
    
    return render(request, 'survey/detail.html', {"survey": survey, "form": form})