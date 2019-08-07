from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
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
    existing_values_achievements_evaluations = {}

    for evaluation in evaluations.all():

        if evaluation.achievement.id in achievements_evaluations.keys():
            existing_values_achievements_evaluations[evaluation.achievement.id].append(evaluation.evaluation_value)

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

        existing_values_achievements_evaluations[evaluation.achievement.id] = [evaluation.evaluation_value]

    return achievements_evaluations, existing_values_achievements_evaluations


def homepage(request):
    return render(request, "homepage.html")


@login_required
@user_passes_test(student_check)
def ues_list(request):
    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre')
    return render(request, "matrix/students/ues_list.html", {"ues":ues})


@login_required
@user_passes_test(student_check)
def matrix_ues(request):
    profile_user = models.ProfileUser.objects.get(user=request.user)

    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre').prefetch_related("ecues__achievements")
    values = models.EvaluationValue.objects.all()

    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, 
        teacher_evaluation=False
    ).prefetch_related('achievement', 'evaluation_value')

    achievements_evaluations, existing_values_achievements_evaluations = _get_achievement_evaluations(evaluations)

    return render(request, "matrix/students/matrix_ues.html", {
        "ues":ues, "values":values,
        "achievements_evaluations": achievements_evaluations, "existing_values_achievements_evaluations": existing_values_achievements_evaluations})


@login_required
@user_passes_test(student_check)
def matrix_ecue(request, slug):
    ecue = models.ECUE.objects.get(slug=slug)
    profile_user = models.ProfileUser.objects.get(user=request.user)
    achievements = models.LearningAchievement.objects.filter(ecue=ecue)
    evaluations = models.StudentEvaluation.objects.filter(
        student=profile_user, 
        teacher_evaluation=False
    ).prefetch_related('achievement', 'evaluation_value')

    achievements_evaluations, _ = _get_achievement_evaluations(evaluations)

    return render(request, "matrix/students/matrix_ecue.html", {
        "ecue":ecue, "achievements":achievements, "evaluations":evaluations, "achievements_evaluations":achievements_evaluations
    })


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


@login_required
@user_passes_test(student_check)
def evaluate_achievement(request, slug):
    achievement = models.LearningAchievement.objects.get(slug=slug)

    student = models.ProfileUser.objects.get(user=request.user)
    try:
        evaluation_existante = models.StudentEvaluation.objects.get(achievement=achievement, student=student, teacher_evaluation=False)
        # return redirect('ues.matrix_ecue', achievement.ecue.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = False
            evaluation_student.save()
            return redirect('ues.matrix_ecue', achievement.ecue.slug)
    else:
        form = forms.StudentEvaluationForm()
    return render(request, "matrix/students/evaluate_achievement.html", {"form":form, "achievement": achievement})


@login_required
@user_passes_test(teacher_check)
def homepage_teachers(request):
    teacher = models.ProfileUser.objects.get(user=request.user)

    classes = models.SmallClass.objects.filter(
        teacher=teacher
    ).prefetch_related('ecue').prefetch_related('students')

    return render(request, "matrix/teachers/homepage.html", {
        "classes": classes            
    })


@login_required
@user_passes_test(student_check)
def evaluate_achievement_student(request, slug, student):
    achievement = models.LearningAchievement.objects.get(slug=slug)

    student = models.ProfileUser.objects.get(user=request.user)
    try:
        evaluation_existante = models.StudentEvaluation.objects.get(achievement=achievement, student=student, teacher_evaluation=False)
        # return redirect('ues.matrix_ecue', achievement.ecue.slug)
    except models.StudentEvaluation.DoesNotExist:
        pass
    except models.StudentEvaluation.MultipleObjectsReturned:
        pass

    if request.method == "POST":
        form = forms.StudentEvaluationForm(request.POST)
        if form.is_valid():
            evaluation_student = form.save(commit=False)
            evaluation_student.achievement = achievement
            evaluation_student.student = student
            evaluation_student.teacher_evaluation = False
            evaluation_student.save()
            return redirect('ues.matrix_ecue', achievement.ecue.slug)
    else:
        form = forms.StudentEvaluationForm()
    return render(request, "matrix/teachers/evaluate_achievement.html", {"form":form, "achievement": achievement})