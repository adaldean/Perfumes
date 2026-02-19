from django import template

register = template.Library()

@register.filter
def add(value, arg):
    """Suma dos números"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value
