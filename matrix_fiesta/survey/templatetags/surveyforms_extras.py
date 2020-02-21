from django import template

register = template.Library()


@register.filter
def get_field(form, key):
    return form[f"question_{key}"]
