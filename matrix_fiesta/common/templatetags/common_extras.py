from django import template

from common.auths import check_is_student, check_is_teacher

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if type(dictionary) == list or type(dictionary) == tuple:
        return dictionary[key]
    else:
        return dictionary.get(key)


@register.filter()
def is_student(user):
    return check_is_student(user)


@register.filter
def is_teacher(user):
    return check_is_teacher(user)