from django import template

register = template.Library()

@register.filter(name='format')
def format(value):
	res = value
	
	if len(value) > 0:
		res = value[1:]
	return res



