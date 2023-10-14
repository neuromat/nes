from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def settings_value(name: str) -> object:
    return getattr(settings, name, "")
