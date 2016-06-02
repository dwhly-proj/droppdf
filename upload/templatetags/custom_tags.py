from django import template

register = template.Library()

@register.filter(name='format_utf8')
def format_utf8(value):
    return value.format('utf8')
