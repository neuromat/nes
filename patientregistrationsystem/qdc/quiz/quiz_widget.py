from django.forms import Widget
from django.utils import formats
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html


class SelectBoxCountries(Widget):
    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = 'BR'
        final_attrs = self.build_attrs(attrs)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html("""<div class="bfh-selectbox bfh-countries" data-name="{0}" data-country="{1}"\
         "{2}"></div>""", force_text(name), force_text(value), flatatt(final_attrs))


class SelectBoxState(Widget):
    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = 'RJ'
        final_attrs = self.build_attrs(attrs)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html("""<div class="bfh-selectbox bfh-states" data-name="{0}" data-state="{1}" {2}></div>""",
                           force_text(name), force_text(value), flatatt(final_attrs))