from enum import Enum
import json

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from matrix.models import ECUE, DatedModel, ProfileUser, PromotionYear, SchoolYear

class Survey(DatedModel):
    name = models.CharField(max_length=150)
    opened = models.BooleanField(default=False)
    ecue = models.ForeignKey(ECUE, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(unique=True)
    promotionyear = models.ForeignKey(
        PromotionYear, on_delete=models.SET_NULL, null=True, default=None,
        blank=True, related_name="+"
    )
    allow_anonymous = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50]
        super(Survey, self).save(*args, **kwargs)

    def __str__(self):
        return _("Survey %s") % self.name

    class Meta:
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")
        ordering = ['ecue', 'name']


class QuestionTypes(Enum):
    TEXTINPUT = 0
    TEXTAREA = 1
    SELECT = 2
    MULTIPLESELECT = 3
    RADIO = 4
    CHECKBOX = 5


class QuestionChoice(models.Model):
    value = models.CharField(max_length=150, null=False)

    def __str__(self):
        return str(self.value)

    class Meta:
        ordering = ['value']
        verbose_name = _("Question choice")
        verbose_name_plural = _("Question choices")

class Question(models.Model):
    question_type = models.PositiveIntegerField(
        choices = ((t.value, t) for t in list(QuestionTypes)),
        default = QuestionTypes.TEXTINPUT
    )
    content = models.TextField(null=False)
    required = models.BooleanField(default=False)
    order = models.IntegerField(null=False, default=0)
    survey = models.ForeignKey(Survey, null=False,
        on_delete=models.CASCADE, related_name="questions")
    choices = models.ManyToManyField(QuestionChoice)

    def __str__(self):
        return _("Question %s") % self.content
    
    def is_iterable(self):
        return self.question_type in [
            QuestionTypes.SELECT.value, 
            QuestionTypes.MULTIPLESELECT.value,
            QuestionTypes.RADIO.value,
            QuestionTypes.CHECKBOX.value
        ]

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['survey', 'order']


class Response(DatedModel):
    survey = models.ForeignKey(Survey, null=False,
        on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(ProfileUser, null=True, on_delete=models.SET_NULL)
    sent = models.BooleanField(default=True)
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return _("Response to %s by %s") % (self.survey, self.user)
    
    class Meta:
        verbose_name = _("Response")
        verbose_name_plural = _("Responses")
        ordering = ['survey', 'user']

    def prepare_answers_for_template(self, questions):
        if not self.answers:
            raise ValueError("The answers are not available yet in current response")
        self.answers_questions = {}
        for answer in self.answers.all():
            self.answers_questions[answer.question.id] = answer.print()

    def prepare_answers_for_form(self, questions):
        if not self.answers:
            raise ValueError("The answers are not available yet in current response")
        self.answers_questions = {}
        for answer in self.answers.all():
            self.answers_questions[answer.question.id] = answer

    def get_answer(self, elt):
        pass
    
        

class Answer(DatedModel):
    response = models.ForeignKey(Response, null=False, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, null=False, on_delete=models.CASCADE)
    value = models.TextField(null=False)
    nb_elements = models.PositiveIntegerField(default=1)
    choices = models.ManyToManyField(QuestionChoice)
    
    def print(self):
        return json.loads(self.value)
    
    def __str__(self):
        return _("Answer to %s (%s)") % (self.question, self.response)
    
    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        ordering = ['question']
