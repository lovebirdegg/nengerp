from django import template
from django.utils.http import urlencode,unquote

register = template.Library()

@register.filter(name='get')
def get(d, k):
    preserved_filters = unquote(d)
    if preserved_filters != '':
        index = preserved_filters.index('=')
        return preserved_filters[index+1:]
    return ''