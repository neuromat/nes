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
        final_attrs = self.build_attrs(attrs)
        if value is None:
            value = ''
        return format_html("""<div class="bfh-selectbox bfh-countries" data-name="{0}" data-country="{1}"\
        "{2}"></div>""", force_text(name), force_text(value), flatatt(final_attrs))


class SelectBoxCountriesDisabled(Widget):

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        final_attrs['value'] = force_text(self._format_value(value))
        if value is None:
            value = ''
        return format_html("""<select class="form-control bfh-countries" data-name="{0}" data-country="{1}"\
        "{2}"></select>""", force_text(name), force_text(value), flatatt(final_attrs))


class SelectBoxState(Widget):

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        if value is None:
            value = ''
        return format_html("""<div class="bfh-selectbox bfh-states" data-name="{0}" data-state="{1}"\
        {2}></div>""", force_text(name), force_text(value), flatatt(final_attrs))


class SelectBoxStateDisabled(Widget):

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        if value is None:
            value = ''
        final_attrs['value'] = force_text(self._format_value(value))
        return format_html("""<select class="form-control bfh-states" data-name="{0}" data-state="{1}"\
        {2}></select>""", force_text(name), force_text(value), flatatt(final_attrs))
