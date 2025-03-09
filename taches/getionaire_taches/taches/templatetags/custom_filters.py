import hashlib
from django import template

register = template.Library()

@register.filter
def make_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()[:15]
