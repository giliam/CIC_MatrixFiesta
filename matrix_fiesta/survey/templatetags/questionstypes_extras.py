from django import template

from survey.models import QuestionTypes

register = template.Library()


@register.filter
def is_of_type(question, type_name):
    return str(QuestionTypes(question.question_type).name) == type_name


@register.filter
def print_question_type(question_type):
    return str(QuestionTypes(question_type).name)
