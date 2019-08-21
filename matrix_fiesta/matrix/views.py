from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Avg, Value, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, reverse
from django.views.decorators.debug import sensitive_post_parameters

from matrix import forms
from matrix import models
from common import auths

"""
Authorizations functions
"""
def teacher_check(user):
    return auths.check_is_teacher(user)


def student_check(user):
    return auths.check_is_student(user)

"""
Useful functions
"""
def _get_achievement_evaluations(evaluations):
    achievements_evaluations = {}
    existing_achiev_eval = {}

    for evaluation in evaluations.all():

        if evaluation.achievement.id in achievements_evaluations.keys():
            existing_achiev_eval[evaluation.achievement.id].append(evaluation.evaluation_value)

            achievements_evaluations[evaluation.achievement.id]["history"].append({
                "value": evaluation.evaluation_value, "date": evaluation.added_date
            })
            continue
        achievements_evaluations[evaluation.achievement.id] = {
            "last": {
                "value": evaluation.evaluation_value, "date": evaluation.added_date
            },
            "history": []
        }

        existing_achiev_eval[evaluation.achievement.id] = [evaluation.evaluation_value]

    return achievements_evaluations, existing_achiev_eval



##
# HOMEPAGE
##

def homepage(request):
    return render(request, "homepage.html")


##
# USER PAGES
##


@sensitive_post_parameters('password')
def log_in(request):
    error = False
    if request.method == "POST":
        form = forms.ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"] # Nous récupérons le nom d'profile_user
            password = form.cleaned_data["password"] # … et le mot de passe
            user = authenticate(username=username, password=password) #Nous vérifions si les données sont correctes
            if user: # Si l'objet renvoyé n'est pas None
                login(request, user) # nous connectons l'profile_user
                return redirect("homepage")
            else: #sinon une erreur sera affichée
                error = True
    else:
        form = forms.ConnexionForm()
    return render(request, 'users/login.html',locals())


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
    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre')
    return render(request, "matrix/students/ues_list.html", {"ues":ues})


@login_required
@user_passes_test(student_check)
def matrix_ues(request):
    profile_user = models.ProfileUser.objects.get(user=request.user)

    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre').prefetch_related("ecues__courses").prefetch_related("ecues__courses__achievements")
    values = models.EvaluationValue.objects.all()

    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, 
        teacher_evaluation=False
    ).prefetch_related('achievement', 'evaluation_value')

    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(evaluations)

    return render(request, "matrix/students/matrix_ues.html", {
        "ues":ues, "values":values,
        "achievements_evaluations": achievements_evaluations, "existing_achiev_eval": existing_achiev_eval})


@login_required
@user_passes_test(student_check)
def matrix_course(request, slug):
    course = models.Course.objects.get(slug=slug)
    profile_user = models.ProfileUser.objects.get(user=request.user)
    achievements = models.LearningAchievement.objects.filter(course=course)
    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, 
        teacher_evaluation=False
    ).prefetch_related('achievement', 'evaluation_value')

    achievements_evaluations, _ = _get_achievement_evaluations(evaluations)

    return render(request, "matrix/students/matrix_course.html", {
        "course":course, "achievements":achievements, "evaluations":evaluations, "achievements_evaluations":achievements_evaluations
    })


@login_required
@user_passes_test(student_check)
def evaluate_achievement(request, slug):
    achievement = models.LearningAchievement.objects.get(slug=slug)

    student = models.ProfileUser.objects.get(user=request.user)
    try:
        evaluation_existante = models.StudentEvaluation.objects.get(achievement=achievement, student=student, teacher_evaluation=False)
        # return redirect('ues.matrix_course', achievement.course.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            models.StudentEvaluation.objects.filter(
                achievement=achievement, student=student, teacher_evaluation=False
            ).update(last_evaluation=False)
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = False
            evaluation_student.last_evaluation = True
            evaluation_student.save()
            return redirect('ues.matrix_course', achievement.course.slug)
    else:
        form = forms.StudentEvaluationForm()
    return render(request, "matrix/students/evaluate_achievement.html", {"form":form, "achievement": achievement})


@login_required
@user_passes_test(student_check)
def self_evaluate_all(request):
    student = models.ProfileUser.objects.get(user=request.user)

    ues = models.UE.objects.all().prefetch_related('ecues', 'semestre', "ecues__courses", "ecues__courses__achievements")
    values = models.EvaluationValue.objects.all()
    # Gets all evaluations on this small class
    evaluations = models.StudentEvaluation.objects.filter(
         student=student, 
         teacher_evaluation=False,
    ).prefetch_related('achievement', 'evaluation_value')

    # Creates the array of existing evaluations
    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(evaluations)

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
                        form.add_achievement_evaluation(achievement, achievements_evaluations[achievement.id]["last"]["value"])
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
                            # Either updates an existing achievement
                            if achievement.id in achievements_evaluations.keys():
                                last_value = achievements_evaluations[achievement.id]["last"]["value"]
                                if last_value == new_value:
                                    models.StudentEvaluation.objects.filter(
                                        achievement=achievement, 
                                        student=student, 
                                        teacher_evaluation=False,
                                    ).update(
                                        last_evaluation=False
                                    )

                                    evaluation = evaluations.get(
                                        teacher_evaluation=False,
                                        achievement=achievement,
                                        student=student,
                                        evaluation_value=new_value
                                    )
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
                                models.StudentEvaluation.objects.filter(
                                    achievement=achievement, student=student, teacher_evaluation=False
                                ).update(last_evaluation=False)
                                evaluation = models.StudentEvaluation()
                                evaluation.achievement = achievement
                                evaluation.student = student
                                evaluation.evaluation_value = new_value
                                evaluation.teacher_evaluation = False
                                evaluation.last_evaluation = True
                                evaluation.save()
            # Then redirects to the status
            return redirect('ues.matrix')

    return render(request, "matrix/students/overall_self_evaluation.html", {
        "ues": ues, "values": values, "student": student,
        "achievements_evaluations": achievements_evaluations, "existing_achiev_eval": existing_achiev_eval,
        "form": form
    })



##
# TEACHER PAGES
##


@login_required
@user_passes_test(teacher_check)
def homepage_teachers(request):
    teacher = models.ProfileUser.objects.get(user=request.user)

    classes = models.SmallClass.objects.filter(
        teacher=teacher
    ).prefetch_related(
        'course', 'course__achievements', 'course__ecue', 'course__ecue__ue', 'course__ecue__ue__semestre', 'students'
    ).all()

    # Gets all evaluations for the classes of the teacher.
    evaluations = models.StudentEvaluation.objects.filter(
        achievement__course__small_classes__in=classes, teacher_evaluation=True, last_evaluation=True
    ).prefetch_related(
        'evaluation_value', 'achievement__course__small_classes', 'student', 'achievement', 'achievement__course', 'achievement__course__ecue', 'achievement__course__ecue__ue'
    ).all()
    
    evaluations_sorted = {}
    for evaluation in evaluations:
        if not evaluation.student.id in evaluations_sorted.keys():
            evaluations_sorted[evaluation.student.id] = []
        evaluations_sorted[evaluation.student.id].append(evaluation)

    averages = {}
    nb_achievements = {}

    for small_class in classes:
        averages[small_class.id] = {}
        nb_achievements[small_class.id] = len(small_class.course.achievements.all())
        
        students = small_class.students.all()

        if nb_achievements[small_class.id] == 0:
            for student in students:
                averages[small_class.id][student.id] = (0.0, 0)
        else:
            for student in students:
                sum_ = 0
                count_ = 0
                for evaluation in evaluations_sorted[student.id]:
                    if small_class in evaluation.achievement.course.small_classes.all():
                        sum_ += evaluation.evaluation_value.integer_value
                        count_ += 1

                sum_ /= nb_achievements[small_class.id]

                # evaluations_this_sc_student = evaluations.filter(student=student, achievement__course__small_classes=small_class
                #     ).aggregate(sum_values=Coalesce(Sum("evaluation_value__integer_value"), Value(0.0)), nb_evals=Count('achievement'))
                averages[small_class.id][student.id] = (
                    sum_,
                    count_
                )

        if len(students) > 0:
            averages[small_class.id]["average"] = sum(map(lambda x: x[0], averages[small_class.id].values()))/len(small_class.students.all())


    return render(request, "matrix/teachers/homepage.html", {
        "classes": classes, "averages": averages, "nb_achievements": nb_achievements
    })


@login_required
@user_passes_test(teacher_check)
def status_student(request, small_class_id, student_id):
    student = models.ProfileUser.objects.get(id=student_id)
    small_class = models.SmallClass.objects.filter(id=small_class_id).prefetch_related(
        "course", "course__achievements"
    ).get(id=small_class_id)

    values = models.EvaluationValue.objects.all()
    evaluations = models.StudentEvaluation.objects.filter(
         student=student, 
         teacher_evaluation=True,
         achievement__course=small_class.course
    ).prefetch_related('achievement', 'evaluation_value')

    print(small_class.course.achievements)

    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(evaluations)

    return render(request, "matrix/teachers/status_student.html", {
        "small_class":small_class, "values": values, "student": student,
        "achievements_evaluations": achievements_evaluations, "existing_achiev_eval": existing_achiev_eval
    })


@login_required
@user_passes_test(teacher_check)
def evaluate_achievement_student(request, small_class_id, student_id, slug):
    achievement = models.LearningAchievement.objects.get(slug=slug)

    student = models.ProfileUser.objects.get(id=student_id)
    
    small_class = models.SmallClass.objects.get(id=small_class_id, teacher__user=request.user, students__id__contains=student.id)
    try:
        evaluation_existante = models.StudentEvaluation.objects.get(achievement=achievement, student=student, teacher_evaluation=True)
        # return redirect('ues.matrix_course', achievement.course.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            models.StudentEvaluation.objects.filter(
                achievement=achievement, student=student, teacher_evaluation=True
            ).update(last_evaluation=False)
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = True
            evaluation_student.last_evaluation = True
            evaluation_student.save()
            return redirect('ues.status_student', small_class_id, student.id)
    else:
        form = forms.StudentEvaluationForm()
    return render(request, "matrix/teachers/evaluate_achievement.html", {
        "form": form, "student": student, "achievement": achievement, "small_class": small_class,
    })


@login_required
@user_passes_test(teacher_check)
def evaluate_student_all(request, small_class_id, student_id):
    student = models.ProfileUser.objects.get(id=student_id)
    teacher = models.ProfileUser.objects.get(user=request.user)
    
    # Checks we are in a small class existing and taught by the user
    small_class = models.SmallClass.objects.filter(
        id=small_class_id
    ).prefetch_related("course", "course__achievements").get(teacher=teacher, id=small_class_id)

    values = models.EvaluationValue.objects.all()
    # Gets all evaluations on this small class
    evaluations = models.StudentEvaluation.objects.filter(
         student=student, 
         teacher_evaluation=True,
         achievement__course=small_class.course
    ).prefetch_related('achievement', 'evaluation_value')

    # Creates the array of existing evaluations
    achievements_evaluations, existing_achiev_eval = _get_achievement_evaluations(evaluations)

    if request.method == "POST":
        form = forms.StudentEvaluationAllForm(request.POST)
    else:
        form = forms.StudentEvaluationAllForm()

    # Adds a field for all achievements
    for achievement in small_class.course.achievements.all():
        if achievement.id in achievements_evaluations.keys():
            form.add_achievement_evaluation(achievement, achievements_evaluations[achievement.id]["last"]["value"])
        else:
            form.add_achievement_evaluation(achievement)

    # Saves eventually the quries
    if request.method == "POST":
        if form.is_valid():
            for achievement in small_class.course.achievements.all():
                new_value = form.get_cleaned_data(achievement)
                # Either updates an existing achievement
                if achievement.id in achievements_evaluations.keys():
                    last_value = achievements_evaluations[achievement.id]["last"]["value"]
                    if last_value == new_value:
                        models.StudentEvaluation.objects.filter(
                            achievement=achievement, 
                            student=student, 
                            teacher_evaluation=True
                        ).update(
                            last_evaluation=False
                        )

                        evaluation = evaluations.get(
                            teacher_evaluation=True,
                            achievement=achievement,
                            student=student,
                            evaluation_value=new_value
                        )
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
                    models.StudentEvaluation.objects.filter(
                        achievement=achievement, student=student, teacher_evaluation=True
                    ).update(last_evaluation=False)
                    evaluation = models.StudentEvaluation()
                    evaluation.achievement = achievement
                    evaluation.student = student
                    evaluation.evaluation_value = new_value
                    evaluation.teacher_evaluation = True
                    evaluation.last_evaluation = True
                    evaluation.save()
            # Then redirects to the status
            return redirect('ues.status_student', small_class_id, student.id)

    return render(request, "matrix/teachers/student_overall_evaluation.html", {
        "small_class":small_class, "values": values, "student": student,
        "achievements_evaluations": achievements_evaluations, "existing_achiev_eval": existing_achiev_eval,
        "form": form
    })

