import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
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
            Q(promotionyear=profile_user.year_entrance) | Q(promotionyear=None),
        )
        responses = models.Response.objects.filter(
            user__user=self.request.user, survey__opened=False
        ).prefetch_related("survey")
        responses_live = models.Response.objects.filter(
            user__user=self.request.user, survey__opened=True
        ).prefetch_related("survey")
        responses_opened = {}
        for response in responses_live.all():
            responses_opened[response.survey.id] = response
        return {
            "surveys": surveys,
            "responses": responses,
            "responses_opened": responses_opened,
        }


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(auths.check_is_de), name="dispatch")
class SurveyListDeView(ListView):
    model = models.Survey
    template_name = "survey/list_de.html"

    def get_queryset(self):
        surveys = models.Survey.objects.all().prefetch_related("responses")
        return {"surveys": surveys}


@login_required
@user_passes_test(auths.check_is_de)
def create_survey_de(request):
    if request.method == "POST":
        form = forms.SurveyCreationForm(request.POST)
        if form.is_valid():
            survey = form.save()
            return redirect(reverse("survey.list_de"))
    else:
        form = forms.SurveyCreationForm()
    return render(request, "survey/creation_de.html", {"form": form})


@login_required
@user_passes_test(auths.check_is_de)
def de_edit_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related(
            "questions", "responses", "questions__choices"
        ),
        Q(id=survey, archived=False),
    )
    if request.method == "POST":
        form = forms.SurveyCreationForm(request.POST, instance=survey)
        if form.is_valid():
            survey = form.save()
            return redirect(reverse("survey.list_de"))
    else:
        form = forms.SurveyCreationForm(instance=survey)
        form_batch = forms.BatchSelectionForm(survey.questions.all())

    return render(
        request,
        "survey/edition_de.html",
        {"form_edition": form, "survey": survey, "form_batch": form_batch},
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_batch_edition_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions", "questions__choices"),
        Q(id=survey, archived=False),
    )
    if request.method == "POST":
        form_batch = forms.BatchSelectionForm(survey.questions.all(), request.POST)
        if form_batch.is_valid():
            action = form_batch.cleaned_data["action"]
            if action == forms.BatchActions.DUPLICATE.value:
                form = forms.BatchDuplicateForm(survey.questions.all(), request.POST)

                if form.is_valid():
                    question_above_id = form.cleaned_data["question_above"]

                    # Case where we choose to put duplicates in front of all questions
                    if int(question_above_id) == 0:
                        question_above_order = -1
                    else:
                        question_above = get_object_or_404(
                            models.Question, Q(id=question_above_id, survey=survey)
                        )
                        question_above_order = question_above.order

                    nb_questions_duplicated = 0
                    for question in survey.questions.all():
                        if form.cleaned_data.get(f"question_{question.id}", False):
                            nb_questions_duplicated += 1

                    models.Question.objects.filter(
                        survey=survey, order__gt=question_above_order
                    ).update(order=F("order") + nb_questions_duplicated)

                    i = 0
                    for question in survey.questions.all():
                        if form.cleaned_data.get(f"question_{question.id}", False):
                            _duplicate_question(question, question_above_order + i + 1)
                            i += 1

                    # Reorders the survey (retrieves it again to fix the survey.questions remanence)
                    survey = get_object_or_404(
                        models.Survey.objects.prefetch_related("questions"),
                        Q(id=survey.id, archived=False),
                    )
                    _reorder_questions(survey)
                    return redirect(reverse("survey.edit_de", args=[survey.id]))

                return render(
                    request,
                    "survey/confirm_batch_de.html",
                    {
                        "survey": survey,
                        "form": form,
                        "message": _(
                            "Do you confirm the duplication of the following questions?"
                        ),
                    },
                )
            elif action == forms.BatchActions.REMOVE.value:
                form = forms.BatchRemoveForm(survey.questions.all(), request.POST)

                if form.is_valid():
                    if form.cleaned_data["confirm"]:
                        for question in survey.questions.all():
                            if form.cleaned_data.get(f"question_{question.id}", False):
                                question.delete()

                        # Reorders the survey (retrieves it again to fix the survey.questions remanence)
                        survey = get_object_or_404(
                            models.Survey.objects.prefetch_related("questions"),
                            Q(id=survey.id, archived=False),
                        )
                        _reorder_questions(survey)
                        return redirect(reverse("survey.edit_de", args=[survey.id]))

                return render(
                    request,
                    "survey/confirm_batch_de.html",
                    {
                        "survey": survey,
                        "form": form,
                        "message": _(
                            "Do you confirm the deletion of the following questions?"
                        ),
                    },
                )
    return redirect(reverse("survey.edit_de", args=[survey.id]))


def _copy_depth_survey(original_questions, new_survey):
    new_questions = {
        q.id: models.Question(
            question_type=q.question_type,
            survey=new_survey,
            content=q.content,
            required=q.required,
            order=q.order,
        )
        for q in original_questions
    }
    models.Question.objects.bulk_create(new_questions.values())
    new_questions = models.Question.objects.filter(survey=new_survey)
    for i, question in enumerate(new_questions):
        question.choices.set(original_questions[i].choices.all())


@login_required
@user_passes_test(auths.check_is_de)
def de_clear_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("responses"),
        Q(id=survey, archived=False),
    )
    if request.method == "POST":
        form = forms.ConfirmationForm(request.POST)
        if form.is_valid():
            survey_clone = models.Survey.objects.prefetch_related("responses").get(
                id=survey.id
            )
            questions = list(survey.questions.all())
            survey.opened = False
            survey.archived = True
            survey.name += f" ({_('archived')})"
            survey.save()

            survey_clone.pk = None
            survey_clone.save()
            _copy_depth_survey(questions, survey_clone)
            return redirect(reverse("survey.list_de"))
    else:
        form = forms.ConfirmationForm()

    return render(request, "survey/confirm_de.html", {"form": form, "survey": survey})


def _reorder_questions(survey):
    i = 0
    for question in survey.questions.all():
        question.order = i
        question.save()
        i += 1


@login_required
@user_passes_test(auths.check_is_de)
def de_reorder_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions"),
        Q(id=survey, archived=False),
    )

    _reorder_questions(survey)

    return redirect(reverse("survey.edit_de", args=[survey.id]))


@login_required
@user_passes_test(auths.check_is_de)
def de_close_survey(request, survey):
    survey = get_object_or_404(models.Survey, Q(id=survey, archived=False))
    survey.opened = not survey.opened
    survey.save()
    return redirect(reverse("survey.list_de"))


@login_required
@user_passes_test(auths.check_is_de)
def de_copy_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions"), Q(id=survey)
    )
    questions = list(survey.questions.all())
    survey.name += f" ({_('copy')})"
    survey.pk = None
    survey.save()
    _copy_depth_survey(questions, survey)
    return redirect(reverse("survey.edit_de", args=[survey.id]))


def _save_choices_iterable_question(form, question):
    # Makes sure the question has already been saved
    question.save()
    choices = form.cleaned_data["choices"].strip().split("\n")
    choices = [c.strip() for c in choices]
    existing_choices = models.QuestionChoice.objects.filter(value__in=choices)

    # We run over the existing choices found to append them to choices
    for choice_found in existing_choices.all():
        # To avoid adding twice (or more!) some choices
        if choice_found.value in choices:
            choices.remove(choice_found.value)
            question.choices.add(choice_found)

    # Adds the choices not found to the database
    for choice_remaining in choices:
        choice = models.QuestionChoice()
        choice.value = choice_remaining
        choice.save()
        question.choices.add(choice)


@login_required
@user_passes_test(auths.check_is_de)
def de_add_question(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions"),
        Q(id=survey, archived=False),
    )
    if request.method == "POST":
        form = forms.QuestionCreationForm(
            request.POST, initial={"order": len(survey.questions.all())}
        )
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            if question.is_iterable():
                _save_choices_iterable_question(form, question)

            question.save()
            return redirect(
                reverse("survey.edit_de", kwargs={"survey": survey.id})
                + f"#question_{question.id}"
            )
    else:
        form = forms.QuestionCreationForm(
            initial={"order": len(survey.questions.all())}
        )
    return render(
        request, "survey/question_form_de.html", {"form": form, "survey": survey}
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_insert_question(request, question, direction):
    relative_question = get_object_or_404(
        models.Question.objects.prefetch_related("survey"),
        Q(id=question, survey__archived=False),
    )
    survey = relative_question.survey
    assert direction in ["above", "below"]
    if direction == "above":
        offset = -1
    elif direction == "below":
        offset = 1

    if request.method == "POST":
        form = forms.QuestionInsertionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.order = max(relative_question.order + offset, 0)

            models.Question.objects.filter(
                survey=survey, order__gte=question.order
            ).update(order=F("order") + 1)

            if question.is_iterable():
                _save_choices_iterable_question(form, question)

            question.save()
            return redirect(
                reverse("survey.edit_de", kwargs={"survey": survey.id})
                + f"#question_{question.id}"
            )
    else:
        form = forms.QuestionInsertionForm()
    return render(
        request, "survey/question_form_de.html", {"form": form, "survey": survey}
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_edit_question(request, question):
    question = get_object_or_404(
        models.Question.objects.prefetch_related("survey"),
        Q(id=question, survey__archived=False),
    )
    if request.method == "POST":
        form = forms.QuestionCreationForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            if question.is_iterable():
                question.save()
                choices = form.cleaned_data["choices"].strip().split("\n")
                choices = [c.strip() for c in choices]

                # Removes the choices not in it anymore and keep the choices not changed
                for already_choice in question.choices.all():
                    if already_choice.value in choices:
                        choices.remove(already_choice.value)
                    else:
                        question.choices.remove(already_choice)

                existing_choices = models.QuestionChoice.objects.filter(
                    value__in=choices
                )

                # We run over the existing choices found to append them to choices
                for choice_found in existing_choices.all():
                    # To avoid adding twice (or more!) some choices
                    if choice_found.value in choices:
                        choices.remove(choice_found.value)
                        question.choices.add(choice_found)

                # Adds the choices not found to the database
                for choice_remaining in choices:
                    choice = models.QuestionChoice()
                    choice.value = choice_remaining
                    choice.save()
                    question.choices.add(choice)

            question.save()
            return redirect(
                reverse("survey.edit_de", kwargs={"survey": question.survey.id})
                + f"#question_{question.id}"
            )
    else:
        form = forms.QuestionCreationForm(
            instance=question,
            initial={"choices": "\n".join([c.value for c in question.choices.all()])},
        )
    return render(
        request,
        "survey/question_form_de.html",
        {"form": form, "survey": question.survey},
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_move_question(request, question, direction):
    question = get_object_or_404(
        models.Question.objects.prefetch_related("survey"),
        Q(id=question, survey__archived=False),
    )
    if direction == "up":
        offset = -1
    elif direction == "down":
        offset = 1
    else:
        return redirect(
            reverse("survey.edit_de", kwargs={"survey": question.survey.id})
        )

    question_concerned = models.Question.objects.get(
        survey__id=question.survey.id, order=question.order + offset
    )
    question.order, question_concerned.order = question_concerned.order, question.order
    question_concerned.save()
    question.save()
    return redirect(
        reverse("survey.edit_de", kwargs={"survey": question.survey.id})
        + f"#question_{question.id}"
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_remove_question(request, question):
    question = get_object_or_404(
        models.Question.objects.prefetch_related("survey"),
        Q(id=question, survey__archived=False),
    )
    if request.method == "POST":
        form = forms.ConfirmationForm(request.POST)
        if form.is_valid():
            models.Question.objects.filter(
                survey=question.survey, order__gte=question.order
            ).update(order=F("order") - 1)
            question.delete()
            return redirect(
                reverse("survey.edit_de", kwargs={"survey": question.survey.id})
            )
    else:
        form = forms.ConfirmationForm()

    return render(
        request, "survey/confirm_de.html", {"form": form, "question": question}
    )


def _duplicate_question(question, new_order=None):
    choices = question.choices.all()
    question.pk = None
    if new_order is None:
        question.order += 1
    else:
        question.order = new_order
    models.Question.objects.filter(
        survey=question.survey, order__gte=question.order
    ).update(order=F("order") + 1)
    question.save()

    # We run over the choices found to append them to choices
    for choice_found in choices:
        question.choices.add(choice_found)


@login_required
@user_passes_test(auths.check_is_de)
def de_duplicate_question(request, question):
    question = get_object_or_404(
        models.Question.objects.prefetch_related("survey"),
        Q(id=question, survey__archived=False),
    )

    _duplicate_question(question)

    return redirect(
        reverse("survey.edit_de", kwargs={"survey": question.survey.id})
        + f"#question_{question.id}"
    )


@login_required
@user_passes_test(auths.check_is_de)
def de_preview_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions", "questions__choices"),
        id=survey,
    )
    questions = survey.questions.all()
    form = forms.ResponseForm(questions, anonymous=survey.allow_anonymous)

    return render(request, "survey/preview_de.html", {"survey": survey, "form": form})


@login_required
@user_passes_test(auths.check_is_de)
def de_results_survey(request, survey):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions", "ecue"), Q(id=survey)
    )
    responses = models.Response.objects.filter(survey=survey).prefetch_related(
        "user", "answers", "answers__question", "answers__question__choices"
    )

    # Needs to handle each question's results
    answers_results = {
        question.id: {
            "iterable": question.is_iterable(),
            "values": [],
            "choices": {c.id: [c, 0] for c in question.choices.all()},
            "authors": [],
            "authors_ids": [],
        }
        for question in survey.questions.all()
    }

    users = set()

    for response in responses.all():
        for answer in response.answers.all():
            if not answers_results[answer.question.id]["iterable"]:
                answers_results[answer.question.id]["values"].append(answer.print())
                if response.anonymous:
                    answers_results[answer.question.id]["authors"].append(
                        _("Anonymous")
                    )
                else:
                    answers_results[answer.question.id]["authors"].append(response.user)
                users.add(response.user.id)
                answers_results[answer.question.id]["authors_ids"].append(
                    response.user.id
                )
            else:
                for choice in answer.choices.all():
                    answers_results[answer.question.id]["choices"][choice.id][1] += 1

    # Retrieves profiles of concerned users to access small classes
    profiles = ProfileUser.objects.filter(id__in=list(users)).prefetch_related(
        "small_classes_student",
        "small_classes_student__teacher",
        "small_classes_student__course",
    )
    profiles_authors = {}
    for profile in profiles.all():
        small_classes_associated = profile.small_classes_student.filter(
            course__ecue=survey.ecue
        )
        if small_classes_associated.exists():
            profiles_authors[profile.id] = small_classes_associated.all()
        else:
            profiles_authors[profile.id] = []

    return render(
        request,
        "survey/detail_de.html",
        {
            "survey": survey,
            "answers_results": answers_results,
            "profiles_authors": profiles_authors,
        },
    )


@login_required
@user_passes_test(auths.check_is_student)
def detail_survey(request, survey):
    profile_user = ProfileUser.objects.get(user=request.user)
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions"),
        Q(id=survey),
        Q(promotionyear=profile_user.year_entrance) | Q(promotionyear=None),
    )
    response = models.Response.objects.filter(
        survey=survey, user__user=request.user
    ).prefetch_related("answers", "answers__question")

    # If already answered, show answer.
    if len(response) >= 1 and len(response.filter(sent=True).all()) >= 1:
        response = response[0]
        response.prepare_answers_for_template(survey.questions.all())
        return render(
            request,
            "survey/answer.html",
            {
                "survey": survey,
                "response": response,
                "QuestionTypes": models.QuestionTypes,
            },
        )
    elif len(response) >= 1:
        response = response[0]
        return answer_survey(request, survey.id, response)
    elif survey.opened:
        return answer_survey(request, survey.id)
    else:
        return redirect(reverse("survey.list"))


@login_required
def answer_survey(request, survey, initial_response=None):
    survey = get_object_or_404(
        models.Survey.objects.prefetch_related("questions", "questions__choices"),
        id=survey,
    )
    questions = survey.questions.all()
    if request.method == "POST":
        form = forms.ResponseForm(
            questions, request.POST, anonymous=survey.allow_anonymous
        )
        if form.is_valid():

            # reorganizes the choices by question
            choices_by_question = {}
            choices_id = set()
            for question in questions.all():
                question_choices = [c.id for c in question.choices.all()]
                choices_id.update(question_choices)
                choices_by_question[question.id] = question_choices
            choices = models.QuestionChoice.objects.filter(id__in=choices_id)
            choices_by_id = {c.id: c for c in choices.all()}

            # if this is not an edition, create a new response
            if initial_response is None:
                response = models.Response()
            else:
                response = initial_response
                answers = {
                    answer.question.id: answer for answer in response.answers.all()
                }

            response.survey = survey
            response.anonymous = (
                survey.allow_anonymous and form.cleaned_data["anonymous"]
            )
            response.user = ProfileUser.objects.get(user=request.user)
            # checks whether it is a saving or submitting action
            response.sent = "submit" in request.POST and not "save" in request.POST
            response.save()

            for question in questions.all():
                raw_answer = form.cleaned_data.get("question_" + str(question.id), None)
                if raw_answer:
                    if initial_response is None or question.id not in answers.keys():
                        answer = models.Answer()
                    else:
                        answer = answers[question.id]
                    answer.response = response
                    answer.question = question
                    answer.save()
                    if question.is_iterable():
                        json_raw_answer = []
                        answer.choices.clear()
                        if not isinstance(raw_answer, list):
                            raw_answer = [int(raw_answer)]
                        for elt in raw_answer:
                            id_elt = int(elt)
                            if id_elt in choices_by_question[question.id]:
                                answer.choices.add(choices_by_id[id_elt])
                                json_raw_answer.append(choices_by_id[id_elt].value)
                            else:
                                raise ValueError(
                                    "Couldn't find elt",
                                    id_elt,
                                    "in choices available",
                                    choices_by_question[question.id],
                                )
                        answer.value = json.dumps(json_raw_answer)
                    else:
                        print("raw_answer", raw_answer)
                        answer.value = json.dumps(raw_answer, ensure_ascii=False)
                        print("answer.value", answer.value)
                        print("json dumps", json.dumps(raw_answer))
                    answer.save()
            return redirect(reverse("survey.list"))
    else:
        if initial_response is None:
            form = forms.ResponseForm(questions, anonymous=survey.allow_anonymous)
        else:
            initial_response.prepare_answers_for_form(questions)
            form = forms.ResponseForm(questions, anonymous=survey.allow_anonymous)
            form.set_initial(initial_response)

    return render(request, "survey/detail.html", {"survey": survey, "form": form})
