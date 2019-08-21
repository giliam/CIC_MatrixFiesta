from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class DatedModel(models.Model):
    added_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "DatedModel"
        abstract = True


class ProfileUser(DatedModel):
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    schoolyear = models.ForeignKey("SchoolYear", on_delete=models.SET_NULL, null=True)

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname.upper())

    class Meta:
        verbose_name = "Utilisateur"

class SchoolYear(DatedModel):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.name.upper())

    class Meta:
        verbose_name = "Annee"
        ordering = ['order']


class Semestre(DatedModel):
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)
    schoolyear = models.ForeignKey(
        SchoolYear, 
        on_delete=models.SET_NULL, null=True,
        related_name="semestres"
    )

    def __str__(self):
        return "%s" % (self.name.upper())

    class Meta:
        verbose_name = "Semestre"
        ordering = ['order']


class UE(DatedModel):
    name = models.CharField(max_length=150)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, related_name="ues", null=True)

    def __str__(self):
        return "%s (%s)" % (self.name.upper(), self.semestre)

    class Meta:
        verbose_name = "UE"
        ordering = ['semestre', 'name']


class ECUE(DatedModel):
    name = models.CharField(max_length=150)
    ue = models.ForeignKey(UE, on_delete=models.SET_NULL, related_name="ecues", null=True)

    def __str__(self):
        return "ECUE %s - %s" % (self.name, self.ue)

    class Meta:
        verbose_name = "ECUE"
        ordering = ['ue', 'name']


class Course(DatedModel):
    name = models.CharField(max_length=150)
    ecue = models.ForeignKey(ECUE, on_delete=models.SET_NULL, related_name="courses", null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.ecue)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Course, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Course"
        ordering = ['ecue', 'name']


class EvaluationValue(DatedModel):
    value = models.CharField(max_length=10)
    integer_value = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "%s" % (self.value)

    class Meta:
        verbose_name = "Valeur"
        ordering = ["order"]


class LearningAchievement(DatedModel):
    name = models.CharField(max_length=150)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name="achievements", null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return "%s : %s" % (self.course, self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(LearningAchievement, self).save(*args, **kwargs)

    def get_field_name(self):
        return "achievement_" + str(self.id)
    
    class Meta:
        verbose_name = "AcquisApprentissage"
        ordering = ["course", "name"]


class StudentEvaluation(DatedModel):
    achievement = models.ForeignKey(LearningAchievement, on_delete=models.CASCADE)
    student = models.ForeignKey(ProfileUser, on_delete=models.CASCADE)
    evaluation_value = models.ForeignKey(EvaluationValue, on_delete=models.SET_NULL, null=True)
    teacher_evaluation = models.BooleanField(default=False)
    last_evaluation = models.BooleanField(default=False)

    def __str__(self):
        return "%s, %s : %s (teacher: %s)" % (self.achievement, self.student, self.evaluation_value, self.teacher_evaluation)

    class Meta:
        verbose_name = "EvaluationEleve"
        ordering = ["-added_date"]


class SmallClass(DatedModel):
    teacher = models.ForeignKey(
        ProfileUser, on_delete=models.SET_NULL, 
        related_name="small_classes_teacher", null=True,
        limit_choices_to={'user__groups__name': 'Enseignants'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="small_classes")
    students = models.ManyToManyField(ProfileUser, related_name="small_classes_student",
        limit_choices_to={'user__groups__name': 'Élèves'})

    def __str__(self):
        return "PC de %s par %s (%d élèves)" % (self.course, self.teacher, self.students.count())

    class Meta:
        verbose_name = "PetiteClasse"
        ordering = ["course"]
