from django import template

from survey.models import QuestionTypes

register = template.Library()


@register.filter
def is_of_type(question, type_name):
    return str(QuestionTypes(question.question_type).name) == type_name
