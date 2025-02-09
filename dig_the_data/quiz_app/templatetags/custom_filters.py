from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None  # or return a default value, e.g., {}
    return dictionary.get(key)