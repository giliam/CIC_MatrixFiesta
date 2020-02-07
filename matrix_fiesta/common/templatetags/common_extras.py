from django import template

from common import auths

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, list) or isinstance(dictionary, tuple):
        return dictionary[key]
    else:
        return dictionary.get(key)


@register.filter
def divide(a, b):
    if b == 0:
        raise ValueError("b should not be null.")
    return a / b


@register.filter()
def is_student(user):
    return auths.check_is_student(user)


@register.filter
def is_teacher(user):
    return auths.check_is_teacher(user)


@register.filter
def is_de(user):
    return auths.check_is_de(user)


@register.filter
def compute_opacity(max_value, current_value):
    if max_value == 0:
        return str(1.0)
    else:
        return str(1.0 - 0.85 * (current_value / max_value))


@register.filter
def is_list(obj):
    return isinstance(obj, list)
