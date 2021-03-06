import datetime
import math

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from common.auths import GroupsNames


class SluggedModel(models.Model):
    slug = models.SlugField(unique=True, max_length=250)
    slug_field_name = "name"

    def save(self, *args, **kwargs):
        unique_slug = slugify(self.__dict__[self.slug_field_name])[:240]
        slug = unique_slug
        unique_num = 1

        while self.__class__.objects.filter(slug=slug).exists():
            slug = unique_slug + str(unique_num)
            unique_num += 1
        self.slug = slug
        models.Model.save(self, *args, **kwargs)

    class Meta:
        abstract = True


class DatedModel(models.Model):
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = _("DatedModel")
        verbose_name_plural = _("DatedModels")
        abstract = True


class SchoolYear(DatedModel):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.name.upper())

    class Meta:
        verbose_name = _("School year")
        verbose_name_plural = _("School years")
        ordering = ["order"]


class PromotionYear(DatedModel):
    name = models.CharField(max_length=150)
    value = models.PositiveIntegerField(default=0)
    current = models.BooleanField(default=False)

    def __str__(self):
        return "%d" % (self.value)

    class Meta:
        verbose_name = _("Promotion year")
        verbose_name_plural = _("Promotion years")
        ordering = ["value"]


class ProfileUser(DatedModel):
    year_entrance = models.ForeignKey(
        PromotionYear, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    cesure = models.BooleanField(default=False)

    cas_user = models.BooleanField(default=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_schoolyear(self, date_considered=None):
        if date_considered is None:
            date_considered = datetime.datetime.now()
        elif isinstance(date_considered, int):
            date_considered = datetime.datetime(date_considered, 10, 1)

        nb_months = date_considered - datetime.datetime(self.year_entrance.value, 8, 20)
        current_schoolyear = int(max(1, math.ceil(nb_months.days / 365)))

        if self.cesure and current_schoolyear > 2:
            current_schoolyear -= 1
        return current_schoolyear

    def __str__(self):
        if len(self.user.first_name) + len(self.user.last_name) == 0:
            return str(self.user)
        else:
            return "%s %s" % (self.user.first_name, self.user.last_name.upper())

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["user__last_name", "user__first_name"]


class Semestre(DatedModel):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)
    schoolyear = models.ForeignKey(
        SchoolYear, on_delete=models.SET_NULL, null=True, related_name="semestres"
    )

    def __str__(self):
        return "%s" % (self.name.upper())

    class Meta:
        verbose_name = _("Semestre")
        verbose_name_plural = _("Semestres")
        ordering = ["order"]


class UE(DatedModel):
    name = models.CharField(max_length=150)
    semestre = models.ForeignKey(
        Semestre, on_delete=models.SET_NULL, related_name="ues", null=True
    )

    def __str__(self):
        return "%s (%s)" % (self.name.upper(), self.semestre)

    class Meta:
        verbose_name = _("UE")
        verbose_name_plural = _("UEs")
        ordering = ["semestre", "name"]


class ECUE(DatedModel):
    name = models.CharField(max_length=150)
    ue = models.ForeignKey(
        UE, on_delete=models.SET_NULL, related_name="ecues", null=True
    )

    def __str__(self):
        return _("ECUE %(name)s - %(ue)s") % {"name": self.name, "ue": self.ue}

    class Meta:
        verbose_name = _("ECUE")
        verbose_name_plural = _("ECUEs")
        ordering = ["ue", "name"]


class Course(DatedModel, SluggedModel):
    name = models.CharField(max_length=150)
    ecue = models.ForeignKey(
        ECUE, on_delete=models.SET_NULL, related_name="courses", null=True
    )
    slug_field_name = "name"

    def __str__(self):
        return "%(name)s - %(ecue)s" % {"name": self.name, "ecue": self.ecue}

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ["ecue", "name"]


class EvaluationValue(DatedModel):
    value = models.CharField(max_length=150)
    integer_value = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    counts_for_average = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.value)

    class Meta:
        verbose_name = _("Evaluation value")
        verbose_name_plural = _("Evaluation values")
        ordering = ["order"]


class LearningAchievement(DatedModel, SluggedModel):
    name = models.CharField(max_length=150)
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, related_name="achievements", null=True
    )
    activated = models.BooleanField(default=True)
    slug_field_name = "name"

    def __str__(self):
        return "%s : %s" % (self.course, self.name)

    def get_field_name(self):
        return "achievement_" + str(self.id)

    class Meta:
        verbose_name = _("Learning achievement")
        verbose_name_plural = _("Learning achievements")
        ordering = ["course", "name"]


class StudentEvaluation(DatedModel):
    achievement = models.ForeignKey(LearningAchievement, on_delete=models.CASCADE)
    student = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, related_name="evaluations_student"
    )
    evaluation_value = models.ForeignKey(
        EvaluationValue, on_delete=models.SET_NULL, null=True
    )
    teacher_evaluation = models.BooleanField(default=False)
    last_evaluation = models.BooleanField(default=False)

    def __str__(self):
        return _("%(achiev)s, %(student)s : %(eval)s (teacher: %(teacher)s)") % {
            "achiev": self.achievement,
            "student": self.student,
            "eval": self.evaluation_value,
            "teacher": self.teacher_evaluation,
        }

    class Meta:
        verbose_name = _("Student evaluation")
        verbose_name_plural = _("Student evaluations")
        ordering = ["-added_date"]


class SmallClass(DatedModel):
    name = models.CharField(max_length=150, null=True, default="")
    teacher = models.ForeignKey(
        ProfileUser,
        on_delete=models.SET_NULL,
        related_name="small_classes_teacher",
        null=True,
        limit_choices_to={"user__groups__name": GroupsNames.TEACHERS_LEVEL.value},
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="small_classes"
    )
    students = models.ManyToManyField(
        ProfileUser,
        related_name="small_classes_student",
        limit_choices_to={"user__groups__name": GroupsNames.STUDENTS_LEVEL.value},
    )
    promotion_year = models.ForeignKey(
        PromotionYear,
        on_delete=models.SET_NULL,
        null=True,
        related_name="small_classes",
    )

    def __str__(self):
        return _("SC %(name)s of %(course)s by %(teacher)s") % {
            "name": self.name,
            "course": self.course,
            "teacher": self.teacher,
        }

    class Meta:
        verbose_name = _("Small class")
        verbose_name_plural = _("Small classes")
        ordering = ["course"]
