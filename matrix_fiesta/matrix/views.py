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

    ues = models.UE.objects.all().prefetch_related('ecues').prefetch_related('semestre').prefetch_related("ecues__achievements")
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


##
# TEACHER PAGES
##


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
@user_passes_test(teacher_check)
def status_student(request, small_class_id, student_id):
    student = models.ProfileUser.objects.get(id=student_id)
    small_class = models.SmallClass.objects.filter(id=small_class_id).prefetch_related("ecue", "ecue__achievements").get(id=small_class_id)
    values = models.EvaluationValue.objects.all()
    evaluations = models.StudentEvaluation.objects.filter(
         student=student, 
         teacher_evaluation=True,
         achievement__ecue=small_class.ecue
    ).prefetch_related('achievement', 'evaluation_value')

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
            evaluation_student.teacher_evaluation = True
            evaluation_student.save()
            return redirect('ues.status_student', small_class_id, student.id)
    else:
        form = forms.StudentEvaluationForm()
    return render(request, "matrix/teachers/evaluate_achievement.html", {
        "form": form, "student": student, "achievement": achievement, "small_class": small_class,
    })

