from io import TextIOWrapper
import csv

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_post_parameters

from matrix import forms
from matrix import models
from common import auths


# Authorizations functions
def teacher_check(user):
    return auths.check_is_teacher(user)


def student_check(user):
    return auths.check_is_student(user)


def de_check(user):
    return auths.check_is_de(user)


# Useful functions
def _get_achievement_evaluations(evaluations):
    achievements_evaluations = {}
    existing_achiev_eval = {}

    for evaluation in evaluations.all():

        if evaluation.achievement.id in achievements_evaluations.keys():
            existing_achiev_eval[evaluation.achievement.id].append(
                evaluation.evaluation_value
            )

            achievements_evaluations[evaluation.achievement.id]["history"].append(
                {"value": evaluation.evaluation_value, "date": evaluation.added_date}
            )
            continue
        achievements_evaluations[evaluation.achievement.id] = {
            "last": {
                "value": evaluation.evaluation_value,
                "date": evaluation.added_date,
            },
            "history": [],
        }

        existing_achiev_eval[evaluation.achievement.id] = [evaluation.evaluation_value]

    for achiev_id, data in achievements_evaluations.items():
        data["history"].sort(key=lambda x: x["date"], reverse=True)
        achievements_evaluations[achiev_id] = data

    return achievements_evaluations, existing_achiev_eval


##
# HOMEPAGE
##


def homepage(request):
    return render(request, "homepage.html")


##
# USER PAGES
##


@sensitive_post_parameters("password")
def log_in(request):
    error = False
    if request.method == "POST":
        form = forms.ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data[
                "username"
            ]  # Nous récupérons le nom d'profile_user
            password = form.cleaned_data["password"]  # … et le mot de passe
            user = authenticate(
                username=username, password=password
            )  # Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'profile_user
                return redirect("homepage")
            else:  # sinon une erreur sera affichée
                error = True
    else:
        if request.user.is_authenticated:
            return redirect("homepage")
        form = forms.ConnexionForm()
    return render(
        request,
        "users/login.html",
        {"form": form, "user": request.user, "error": error},
    )


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse(log_in))


##
# STUDENT PAGES
##


@login_required
@user_passes_test(student_check)
def ues_list(request):
    ues = models.UE.objects.all().prefetch_related("ecues").prefetch_related("semestre")
    return render(request, "matrix/students/ues_list.html", {"ues": ues})


@login_required
@user_passes_test(student_check)
def matrix_ues(request, archives=None):
    profile_user = models.ProfileUser.objects.get(user=request.user)

    promotion_years = models.PromotionYear.objects.filter(
        value__gte=profile_user.year_entrance.value, current=False
    )

    if not archives is None:
        archives = int(archives)

    ues = models.UE.objects.filter(
        semestre__schoolyear__order=profile_user.get_schoolyear(archives)
    ).prefetch_related(
        "ecues", "semestre", "ecues__courses", "ecues__courses__achievements"
    )
    values = models.EvaluationValue.objects.all()

    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, teacher_evaluation=False
    ).prefetch_related("achievement", "evaluation_value")

    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(
        evaluations
    )

    return render(
        request,
        "matrix/students/matrix_ues.html",
        {
            "ues": ues,
            "values": values,
            "achievements_evaluations": achievements_evaluations,
            "existing_achiev_eval": existing_achiev_eval,
            "promotion_years": promotion_years,
            "archives": archives,
        },
    )


@login_required
@user_passes_test(student_check)
def matrix_course(request, slug):
    profile_user = models.ProfileUser.objects.get(user=request.user)
    course = models.Course.objects.get(
        slug=slug, ecue__ue__semestre__schoolyear__order=profile_user.get_schoolyear()
    )
    achievements = models.LearningAchievement.objects.filter(
        course=course, activated=True
    )
    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, teacher_evaluation=False
    ).prefetch_related("achievement", "evaluation_value")

    achievements_evaluations, _ = _get_achievement_evaluations(evaluations)

    return render(
        request,
        "matrix/students/matrix_course.html",
        {
            "course": course,
            "achievements": achievements,
            "evaluations": evaluations,
            "achievements_evaluations": achievements_evaluations,
        },
    )


@login_required
@user_passes_test(student_check)
def evaluate_course(request, slug):
    student = models.ProfileUser.objects.get(user=request.user)
    course = models.Course.objects.get(
        slug=slug, ecue__ue__semestre__schoolyear__order=student.get_schoolyear()
    )
    achievements = models.LearningAchievement.objects.filter(course=course)
    evaluations = models.StudentEvaluation.objects.filter(
        student=student, teacher_evaluation=False
    ).prefetch_related("achievement", "evaluation_value")
    values = models.EvaluationValue.objects.all()

    achievements_evaluations, _ = _get_achievement_evaluations(evaluations)

    if request.method == "POST":
        form = forms.StudentEvaluationAllForm(request.POST)
    else:
        form = forms.StudentEvaluationAllForm()

    # Adds a field for all achievements
    for achievement in course.achievements.all():
        if achievement.id in achievements_evaluations.keys():
            form.add_achievement_evaluation(
                achievement, achievements_evaluations[achievement.id]["last"]["value"]
            )
        else:
            form.add_achievement_evaluation(achievement)

    # Saves eventually the quries
    if request.method == "POST":
        if form.is_valid():
            for achievement in course.achievements.all():
                new_value = form.get_cleaned_data(achievement)

                if new_value is None:
                    continue

                # sets all previous evaluation to false
                models.StudentEvaluation.objects.filter(
                    achievement=achievement, student=student, teacher_evaluation=False
                ).update(last_evaluation=False)

                # Either updates an existing achievement
                if achievement.id in achievements_evaluations.keys():
                    last_value = achievements_evaluations[achievement.id]["last"][
                        "value"
                    ]
                    if last_value == new_value:
                        evaluation_same = evaluations.filter(
                            teacher_evaluation=False,
                            achievement=achievement,
                            student=student,
                            evaluation_value=new_value,
                        )
                        evaluation = evaluation_same.all()[0]
                    else:
                        evaluation = models.StudentEvaluation()
                        evaluation.achievement = achievement
                        evaluation.student = student
                        evaluation.evaluation_value = new_value
                        evaluation.teacher_evaluation = False
                    evaluation.last_evaluation = True
                    evaluation.save()
                # Or creates a new one
                else:
                    evaluation = models.StudentEvaluation()
                    evaluation.achievement = achievement
                    evaluation.student = student
                    evaluation.evaluation_value = new_value
                    evaluation.teacher_evaluation = False
                    evaluation.last_evaluation = True
                    evaluation.save()
            # Then redirects to the status
            return redirect("ues.matrix_course", course.slug)

    return render(
        request,
        "matrix/students/course_self_evaluation.html",
        {
            "course": course,
            "achievements": achievements,
            "evaluations": evaluations,
            "achievements_evaluations": achievements_evaluations,
            "form": form,
            "values": values,
        },
    )


@login_required
@user_passes_test(student_check)
def evaluate_achievement(request, slug):
    student = models.ProfileUser.objects.get(user=request.user)

    achievement = models.LearningAchievement.objects.get(
        slug=slug,
        course__ecue__ue__semestre__schoolyear__order=student.get_schoolyear(),
    )

    try:
        models.StudentEvaluation.objects.get(
            achievement=achievement, student=student, teacher_evaluation=False
        )
        # return redirect('ues.matrix_course', achievement.course.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            # sets all previous evaluation to false
            models.StudentEvaluation.objects.filter(
                achievement=achievement, student=student, teacher_evaluation=False
            ).update(last_evaluation=False)
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = False
            evaluation_student.last_evaluation = True
            evaluation_student.save()
            return redirect("ues.matrix_course", achievement.course.slug)
    else:
        form = forms.StudentEvaluationForm()
    return render(
        request,
        "matrix/students/evaluate_achievement.html",
        {"form": form, "achievement": achievement},
    )


@login_required
@user_passes_test(student_check)
def self_evaluate_all(request):
    student = models.ProfileUser.objects.get(user=request.user)

    ues = models.UE.objects.filter(
        semestre__schoolyear__order=student.get_schoolyear()
    ).prefetch_related(
        "ecues", "semestre", "ecues__courses", "ecues__courses__achievements"
    )
    values = models.EvaluationValue.objects.all()
    # Gets all evaluations on this small class
    evaluations = models.StudentEvaluation.objects.filter(
        student=student, teacher_evaluation=False
    ).prefetch_related("achievement", "evaluation_value")

    # Creates the array of existing evaluations
    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(
        evaluations
    )

    if request.method == "POST":
        form = forms.StudentEvaluationAllForm(request.POST)
    else:
        form = forms.StudentEvaluationAllForm()

    # Adds a field for all achievements
    for ue in ues.all():
        for ecue in ue.ecues.all():
            for course in ecue.courses.all():
                for achievement in course.achievements.all():
                    if achievement.id in achievements_evaluations.keys():
                        form.add_achievement_evaluation(
                            achievement,
                            achievements_evaluations[achievement.id]["last"]["value"],
                        )
                    else:
                        form.add_achievement_evaluation(achievement)

    # Saves eventually the quries
    if request.method == "POST":
        if form.is_valid():
            for ue in ues.all():
                for ecue in ue.ecues.all():
                    for course in ecue.courses.all():
                        for achievement in course.achievements.all():
                            new_value = form.get_cleaned_data(achievement)

                            if new_value is None:
                                continue

                            # sets all previous evaluation to false
                            models.StudentEvaluation.objects.filter(
                                achievement=achievement,
                                student=student,
                                teacher_evaluation=False,
                            ).update(last_evaluation=False)

                            # Either updates an existing achievement
                            if achievement.id in achievements_evaluations.keys():
                                last_value = achievements_evaluations[achievement.id][
                                    "last"
                                ]["value"]
                                if last_value == new_value:

                                    evaluation_same = evaluations.filter(
                                        teacher_evaluation=False,
                                        achievement=achievement,
                                        student=student,
                                        evaluation_value=new_value,
                                    )
                                    evaluation = evaluation_same.all()[0]
                                else:
                                    evaluation = models.StudentEvaluation()
                                    evaluation.achievement = achievement
                                    evaluation.student = student
                                    evaluation.evaluation_value = new_value
                                    evaluation.teacher_evaluation = False
                                evaluation.last_evaluation = True
                                evaluation.save()
                            # Or creates a new one
                            else:
                                evaluation = models.StudentEvaluation()
                                evaluation.achievement = achievement
                                evaluation.student = student
                                evaluation.evaluation_value = new_value
                                evaluation.teacher_evaluation = False
                                evaluation.last_evaluation = True
                                evaluation.save()
            # Then redirects to the status
            return redirect("ues.matrix")

    return render(
        request,
        "matrix/students/overall_self_evaluation.html",
        {
            "ues": ues,
            "values": values,
            "student": student,
            "achievements_evaluations": achievements_evaluations,
            "existing_achiev_eval": existing_achiev_eval,
            "form": form,
        },
    )


##
# TEACHER PAGES
##


def _compute_averages(evaluations, classes):
    evaluations_sorted = {}
    for evaluation in evaluations:
        if not evaluation.student.id in evaluations_sorted.keys():
            evaluations_sorted[evaluation.student.id] = []
        evaluations_sorted[evaluation.student.id].append(evaluation)

    averages = {}
    nb_achievements = {}

    for small_class in classes:
        averages[small_class.id] = {}
        nb_achievements[small_class.id] = small_class.course.achievements.count()

        students = small_class.students.all()

        if nb_achievements[small_class.id] == 0:
            for student in students:
                averages[small_class.id][student.id] = (0.0, 0)
        else:
            for student in students:
                sum_ = 0
                count_ = 0
                if student.id in evaluations_sorted.keys():
                    for evaluation in evaluations_sorted[student.id]:
                        if (
                            small_class
                            in evaluation.achievement.course.small_classes.all()
                        ) and evaluation.evaluation_value.counts_for_average:
                            sum_ += evaluation.evaluation_value.integer_value
                            count_ += 1

                # sum_ /= nb_achievements[small_class.id]
                if count_ > 0:
                    sum_ /= count_
                else:
                    sum_ = 0.0

                # evaluations_this_sc_student = evaluations.filter(student=student, achievement__course__small_classes=small_class
                #     ).aggregate(sum_values=Coalesce(Sum("evaluation_value__integer_value"), Value(0.0)), nb_evals=Count('achievement'))
                averages[small_class.id][student.id] = (sum_, count_)

        # If there is any student, computes the average
        if len(students) > 0:
            averages[small_class.id]["average"] = (
                sum(map(lambda x: x[0], averages[small_class.id].values()))
                / small_class.students.count()
            )

    return averages, nb_achievements


@login_required
@user_passes_test(teacher_check)
def homepage_teachers(request, archives=None):
    teacher = models.ProfileUser.objects.get(user=request.user)

    if not archives is None:
        archives = int(archives)

        classes = (
            models.SmallClass.objects.filter(
                promotion_year__value=archives, teacher=teacher
            )
            .prefetch_related(
                "course",
                "course__achievements",
                "course__ecue",
                "course__ecue__ue",
                "course__ecue__ue__semestre",
                "students",
                "students__user",
            )
            .all()
        )
    else:
        classes = (
            models.SmallClass.objects.filter(
                promotion_year__current=True, teacher=teacher
            )
            .prefetch_related(
                "course",
                "course__achievements",
                "course__ecue",
                "course__ecue__ue",
                "course__ecue__ue__semestre",
                "students",
                "students__user",
            )
            .all()
        )

    # Gets all evaluations for the classes of the teacher.
    evaluations = (
        models.StudentEvaluation.objects.filter(
            achievement__course__small_classes__in=classes,
            teacher_evaluation=True,
            last_evaluation=True,
        )
        .prefetch_related(
            "evaluation_value",
            "achievement__course__small_classes",
            "student",
            "student__user",
            "achievement",
            "achievement__course",
        )
        .all()
    )

    # Gets all evaluations for the classes of the students.
    evaluations_students = (
        models.StudentEvaluation.objects.filter(
            achievement__course__small_classes__in=classes,
            teacher_evaluation=False,
            last_evaluation=True,
        )
        .prefetch_related(
            "evaluation_value",
            "achievement__course__small_classes",
            "student",
            "student__user",
            "achievement",
            "achievement__course",
        )
        .all()
    )

    averages, nb_achievements = _compute_averages(evaluations, classes)
    averages_students, nb_achievements_students = _compute_averages(
        evaluations_students, classes
    )

    promotion_years = models.PromotionYear.objects.filter(current=False)

    return render(
        request,
        "matrix/teachers/homepage.html",
        {
            "classes": classes,
            "averages": averages,
            "nb_achievements": nb_achievements,
            "averages_students": averages_students,
            "nb_achievements_students": nb_achievements_students,
            "archives": archives,
            "promotion_years": promotion_years,
        },
    )


@login_required
@user_passes_test(teacher_check)
def status_student(request, small_class_id, student_id):
    student = models.ProfileUser.objects.get(id=student_id)
    small_class = (
        models.SmallClass.objects.filter(id=small_class_id)
        .prefetch_related("course", "course__achievements")
        .get(id=small_class_id)
    )

    values = models.EvaluationValue.objects.all()
    evaluations = models.StudentEvaluation.objects.filter(
        student=student, teacher_evaluation=True, achievement__course=small_class.course
    ).prefetch_related("achievement", "evaluation_value")
    evaluations_student = models.StudentEvaluation.objects.filter(
        student=student,
        teacher_evaluation=False,
        achievement__course=small_class.course,
    ).prefetch_related("achievement", "evaluation_value")

    achiev_eval, existing_eval = _get_achievement_evaluations(evaluations)
    achiev_eval_student, existing_eval_student = _get_achievement_evaluations(
        evaluations_student
    )

    return render(
        request,
        "matrix/teachers/status_student.html",
        {
            "small_class": small_class,
            "values": values,
            "student": student,
            "achiev_eval": achiev_eval,
            "existing_eval": existing_eval,
            "achiev_eval_student": achiev_eval_student,
            "existing_eval_student": existing_eval_student,
        },
    )


@login_required
@user_passes_test(teacher_check)
def evaluate_achievement_student(request, small_class_id, student_id, slug):
    achievement = models.LearningAchievement.objects.get(slug=slug)

    student = models.ProfileUser.objects.get(id=student_id)

    small_class = models.SmallClass.objects.get(
        id=small_class_id, teacher__user=request.user, students__id__contains=student.id
    )
    try:
        models.StudentEvaluation.objects.get(
            achievement=achievement, student=student, teacher_evaluation=True
        )
        # return redirect('ues.matrix_course', achievement.course.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            # sets all previous evaluation to false
            models.StudentEvaluation.objects.filter(
                achievement=achievement, student=student, teacher_evaluation=True
            ).update(last_evaluation=False)
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = True
            evaluation_student.last_evaluation = True
            evaluation_student.save()
            return redirect("teachers.status_student", small_class_id, student.id)
    else:
        form = forms.StudentEvaluationForm()
    return render(
        request,
        "matrix/teachers/evaluate_achievement.html",
        {
            "form": form,
            "student": student,
            "achievement": achievement,
            "small_class": small_class,
        },
    )


@login_required
@user_passes_test(teacher_check)
def evaluate_student_all(request, small_class_id, student_id):
    student = models.ProfileUser.objects.get(id=student_id)
    teacher = models.ProfileUser.objects.get(user=request.user)

    # Checks we are in a small class existing and taught by the user
    small_class = (
        models.SmallClass.objects.filter(id=small_class_id)
        .prefetch_related("course", "course__achievements")
        .get(teacher=teacher, id=small_class_id)
    )

    values = models.EvaluationValue.objects.all()
    # Gets all evaluations on this small class
    evaluations = models.StudentEvaluation.objects.filter(
        student=student, teacher_evaluation=True, achievement__course=small_class.course
    ).prefetch_related("achievement", "evaluation_value")

    # Creates the array of existing evaluations
    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(
        evaluations
    )

    if request.method == "POST":
        form = forms.StudentEvaluationAllForm(request.POST)
    else:
        form = forms.StudentEvaluationAllForm()

    # Adds a field for all achievements
    for achievement in small_class.course.achievements.all():
        if achievement.id in achievements_evaluations.keys():
            form.add_achievement_evaluation(
                achievement, achievements_evaluations[achievement.id]["last"]["value"]
            )
        else:
            form.add_achievement_evaluation(achievement)

    # Saves eventually the quries
    if request.method == "POST":
        if form.is_valid():
            for achievement in small_class.course.achievements.all():
                new_value = form.get_cleaned_data(achievement)

                if new_value is None:
                    continue

                # sets all previous evaluation to false
                models.StudentEvaluation.objects.filter(
                    achievement=achievement, student=student, teacher_evaluation=True
                ).update(last_evaluation=False)

                # Either updates an existing achievement
                if achievement.id in achievements_evaluations.keys():
                    last_value = achievements_evaluations[achievement.id]["last"][
                        "value"
                    ]
                    if last_value == new_value:
                        evaluation_same = evaluations.filter(
                            teacher_evaluation=True,
                            achievement=achievement,
                            student=student,
                            evaluation_value=new_value,
                        )
                        evaluation = evaluation_same.all()[0]
                    else:
                        evaluation = models.StudentEvaluation()
                        evaluation.achievement = achievement
                        evaluation.student = student
                        evaluation.evaluation_value = new_value
                        evaluation.teacher_evaluation = True
                    evaluation.last_evaluation = True
                    evaluation.save()
                # Or creates a new one
                else:
                    evaluation = models.StudentEvaluation()
                    evaluation.achievement = achievement
                    evaluation.student = student
                    evaluation.evaluation_value = new_value
                    evaluation.teacher_evaluation = True
                    evaluation.last_evaluation = True
                    evaluation.save()
            # Then redirects to the status
            return redirect("teachers.status_student", small_class_id, student.id)

    return render(
        request,
        "matrix/teachers/student_overall_evaluation.html",
        {
            "small_class": small_class,
            "values": values,
            "student": student,
            "achievements_evaluations": achievements_evaluations,
            "existing_achiev_eval": existing_achiev_eval,
            "form": form,
        },
    )


##
# DE PAGES
##


@login_required
@user_passes_test(de_check)
def homepage_de(request):
    return render(request, "de/homepage.html", {})


@login_required
@user_passes_test(de_check)
def start_new_year(request):
    return render(request, "de/start_new_year.html", {})


@login_required
@user_passes_test(de_check)
def list_users(request, group_filter=auths.GroupsNames.STUDENTS_LEVEL):
    if not isinstance(group_filter, auths.GroupsNames):
        return render(request, "de/homepage.html", {})

    students = models.ProfileUser.objects.filter(
        user__groups__name__contains=group_filter.value
    ).prefetch_related("user", "year_entrance", "user__groups")
    return render(request, "de/list_users.html", {"students": students})


@login_required
@user_passes_test(de_check)
def insert_new_users(request):
    if not request.user.is_superuser:
        raise HttpResponseForbidden(_("Only super users can perform this action"))

    columns = {
        "Firstname": {"index": 0},
        "Lastname": {"index": 1},
        "Email": {"index": 2},
        "Entrance year": {
            "index": 3,
            # sous la forme 20XX
            "help": _("formatted as 20XX"),
        },
        "Cesure": {
            "index": 4,
            # "doit être 0 ou 1"
            "help": _("must be 0 or 1"),
        },
    }

    # Handle file upload
    if request.method == "POST":
        form = forms.UploadNewStudentsForm(request.POST, request.FILES)
        if form.is_valid():
            email_index = columns["Email"]["index"]
            firstname_index = columns["Firstname"]["index"]
            lastname_index = columns["Lastname"]["index"]
            year_entrance_index = columns["Entrance year"]["index"]
            cesure_index = columns["Cesure"]["index"]

            header_skipped = False

            # Reads file uploaded
            # cf. https://stackoverflow.com/a/16243182/8980220
            f = TextIOWrapper(request.FILES["file"].file, encoding="utf-8")
            spamreader = csv.reader(f, delimiter=";")

            if "DE" in form.cleaned_data["group"]:
                raise ValueError(_("DE shouldn't be in the groups selected"))
            else:
                entrance_years = {}

                for student in spamreader:
                    if not header_skipped and form.cleaned_data["has_header"]:
                        header_skipped = True
                        continue

                    username = student[email_index].split("@")[0]

                    user = User.objects.create_user(username, student[email_index], "")
                    user.first_name = student[firstname_index]
                    user.last_name = student[lastname_index]
                    user.groups.set(form.cleaned_data["group"])
                    user.save()

                    profile_user = models.ProfileUser()
                    # gets the object from entrance year
                    entrance_year = student[year_entrance_index]
                    if not entrance_year in entrance_years.keys():
                        entrance_years[
                            entrance_year
                        ] = models.PromotionYear.objects.get(value=entrance_year)
                    profile_user.year_entrance = entrance_years[entrance_year]
                    if len(student) < (cesure_index + 1):
                        profile_user.cesure = False
                    else:
                        profile_user.cesure = student[cesure_index] == 1
                    profile_user.user = user
                    profile_user.save()

            return redirect(reverse("de.list_students"))
    else:
        form = forms.UploadNewStudentsForm()  # A empty, unbound form

    return render(
        request, "de/insert_new_users.html", {"columns": columns, "form": form}
    )


def get_users_from_mails(file_bin, level, email_index, group_index, has_header=False):
    header_skipped = False
    users = {}

    # Reads file uploaded
    # cf. https://stackoverflow.com/a/16243182/8980220
    f = TextIOWrapper(file_bin, encoding="utf-8")
    spamreader = csv.reader(f, delimiter=";")

    # Sorts users to have access to their group
    for student in spamreader:
        if not header_skipped and has_header:
            header_skipped = True
            continue

        email_value = student[email_index]
        group_value = student[group_index]

        users[email_value] = group_value

    profile_users = models.ProfileUser.objects.filter(
        user__email__in=users.keys(), user__groups__name__contains=level.value
    ).prefetch_related("user")

    groups = {}
    for student in profile_users.all():
        group_value = users[student.user.email]

        if not group_value in groups.keys():
            groups[group_value] = []

        groups[group_value].append(student)

    return groups


@login_required
@user_passes_test(de_check)
def create_small_classes(request):
    columns = {"Email": {"index": 0}, "Groupe": {"index": 1}}

    # Handle file upload
    if request.method == "POST":
        form = forms.UploadSmallClassesForm(request.POST, request.FILES)
        if form.is_valid():
            email_index = columns["Email"]["index"]
            group_index = columns["Groupe"]["index"]

            # Creates the groups of profiles_students
            groups_students = get_users_from_mails(
                request.FILES["file_students"].file,
                auths.GroupsNames.STUDENTS_LEVEL,
                email_index,
                group_index,
                form.cleaned_data["has_header"],
            )

            # And creates the teachers' group.
            if not request.FILES.get("file_teachers", None) is None:
                groups_teachers = get_users_from_mails(
                    request.FILES["file_teachers"].file,
                    auths.GroupsNames.TEACHERS_LEVEL,
                    email_index,
                    group_index,
                    form.cleaned_data["has_header"],
                )

            small_class = form.save(commit=False)

            total_classified_students = 0

            for group_id in groups_students.keys():
                small_class.pk = None
                small_class.name = _("Groupe #%d" % int(group_id))

                if group_id in groups_teachers.keys():
                    small_class.teacher = groups_teachers[group_id][0]

                small_class.save()
                small_class.students.set(groups_students[group_id])
                small_class.save()

                total_classified_students += len(groups_students[group_id])

            return redirect(reverse("de.homepage_de"))
    else:
        form = forms.UploadSmallClassesForm()  # A empty, unbound form

    return render(
        request, "de/insert_small_classes.html", {"columns": columns, "form": form}
    )


@login_required
@user_passes_test(teacher_check)
def all_small_classes(request):
    if not request.user.is_superuser:
        raise HttpResponseForbidden(_("Only super users can perform this action"))

    classes = models.SmallClass.objects.filter(
        promotion_year__current=True
    ).prefetch_related(
        "course",
        "course__achievements",
        "course__ecue",
        "course__ecue__ue",
        "course__ecue__ue__semestre",
        "students",
        "students__user",
        "teacher",
        "teacher__user",
    )

    # Gets all evaluations for the classes of the teacher.
    evaluations = (
        models.StudentEvaluation.objects.filter(
            teacher_evaluation=True, last_evaluation=True
        )
        .prefetch_related(
            "evaluation_value",
            "achievement__course__small_classes",
            "student",
            "student__user",
            "achievement",
            "achievement__course",
            "achievement__course__ecue",
            "achievement__course__ecue__ue",
        )
        .all()
    )

    evaluations_sorted = {}
    for evaluation in evaluations:
        if not evaluation.student.id in evaluations_sorted.keys():
            evaluations_sorted[evaluation.student.id] = []
        evaluations_sorted[evaluation.student.id].append(evaluation)

    averages = {}
    nb_achievements = {}

    for small_class in classes:
        averages[small_class.id] = {}
        nb_achievements[small_class.id] = small_class.course.achievements.count()

        students = small_class.students.all()

        if nb_achievements[small_class.id] == 0:
            for student in students:
                averages[small_class.id][student.id] = (0.0, 0)
        else:
            for student in students:
                sum_ = 0
                count_ = 0
                if student.id in evaluations_sorted.keys():
                    for evaluation in evaluations_sorted[student.id]:
                        if (
                            small_class
                            in evaluation.achievement.course.small_classes.all()
                        ) and evaluation.evaluation_value.counts_for_average:
                            sum_ += evaluation.evaluation_value.integer_value
                            count_ += 1

                # sum_ /= nb_achievements[small_class.id]
                if count_ > 0:
                    sum_ /= count_
                else:
                    sum_ = 0.0

                # evaluations_this_sc_student = evaluations.filter(student=student, achievement__course__small_classes=small_class
                #     ).aggregate(sum_values=Coalesce(Sum("evaluation_value__integer_value"), Value(0.0)), nb_evals=Count('achievement'))
                averages[small_class.id][student.id] = (sum_, count_)

        if len(students) > 0:
            averages[small_class.id]["average"] = (
                sum(map(lambda x: x[0], averages[small_class.id].values()))
                / small_class.students.count()
            )

    return render(
        request,
        "matrix/teachers/list_all_sc.html",
        {"classes": classes, "averages": averages, "nb_achievements": nb_achievements},
    )


@login_required
@user_passes_test(teacher_check)
def all_students(request, schoolyear=1):
    if not request.user.is_superuser:
        raise HttpResponseForbidden(_("Only super users can perform this action"))

    # Converts the schoolyear
    schoolyear = int(schoolyear)

    ues = models.UE.objects.filter(
        semestre__schoolyear__order=schoolyear
    ).prefetch_related(
        "ecues", "semestre", "ecues__courses", "ecues__courses__achievements"
    )

    # Gets all evaluations for the classes of the teacher.
    evaluations = (
        models.StudentEvaluation.objects.filter(
            teacher_evaluation=True,
            last_evaluation=True,
            achievement__course__ecue__ue__in=ues,
        )
        .prefetch_related(
            "evaluation_value",
            "achievement__course__small_classes",
            "student",
            "student__user",
            "student__year_entrance",
            "achievement",
            "achievement__course",
            "achievement__course__ecue",
            "achievement__course__ecue__ue",
        )
        .all()
    )

    all_students = models.ProfileUser.objects.filter(
        user__groups__name__contains=auths.GroupsNames.STUDENTS_LEVEL.value
    ).prefetch_related("year_entrance", "user")
    students = {}
    for student in all_students:
        if student.get_schoolyear() == schoolyear:
            students[student.id] = student

    evaluations_sorted = {}
    for evaluation in evaluations:
        student_id = evaluation.student.id
        ue_id = evaluation.achievement.course.ecue.ue.id

        if not student_id in evaluations_sorted.keys():
            evaluations_sorted[student_id] = {}
        if not ue_id in evaluations_sorted[student_id].keys():
            evaluations_sorted[student_id][ue_id] = {"count": 0.0, "sum": 0.0}

        if evaluation.evaluation_value.counts_for_average:
            evaluations_sorted[student_id][ue_id]["count"] += 1.0
            evaluations_sorted[student_id][ue_id][
                "sum"
            ] += evaluation.evaluation_value.integer_value

    school_years = models.SchoolYear.objects.filter()

    return render(
        request,
        "matrix/teachers/list_all_students.html",
        {
            "ues": ues,
            "evaluations_sorted": evaluations_sorted,
            "students": students,
            "school_years": school_years,
        },
    )


def error_404(request, exception):
    return render(request, "error/404.html")


def error_500(request):
    return render(request, "error/500.html")


def error_403(request, exception):
    return render(request, "error/403.html")


def error_400(request, exception):
    return render(request, "error/400.html")
