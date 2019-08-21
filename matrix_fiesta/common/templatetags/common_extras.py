from django import template

from common import auths

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if type(dictionary) == list or type(dictionary) == tuple:
        return dictionary[key]
    else:
        return dictionary.get(key)


@register.filter()
def is_student(user):
    return auths.check_is_student(user)


@register.filter
def is_teacher(user):
    return auths.check_is_teacher(user)


@register.filter
def is_de(user):
    return auths.check_is_de(user)