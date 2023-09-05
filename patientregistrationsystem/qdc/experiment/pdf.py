import os

from html import escape
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from io import BytesIO

from qdc import settings


def fetch_resources(uri, rel):
    static_url = settings.STATIC_URL
    static_root = settings.STATIC_ROOT
    media_url = settings.MEDIA_URL
    media_root = settings.MEDIA_ROOT

    # convert URIs to absolute system paths
    if uri.startswith(media_url):
        path = os.path.join(media_root, uri.replace(media_url, ""))
    elif uri.startswith(static_url):
        path = os.path.join(static_root, uri.replace(static_url, ""))
    else:
        return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception("media URI must start with %s or %s" % (static_url, media_url))

    return path


def render(template_src, context_dict, css_source=None):
    template = get_template(template_src)
    # context = Context(context_dict)
    html = template.render(context_dict)
    result = BytesIO()

    if css_source:
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            dest=result,
            encoding="UTF-8",
            link_callback=fetch_resources,
            default_css=open(
                os.path.join(settings.BASE_DIR, "static", "css", css_source)
            ).read(),
        )
    else:
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            dest=result,
            encoding="UTF-8",
            link_callback=fetch_resources,
        )

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")

    return HttpResponse("_(We had some errors<pre>%s</pre>)" % escape(html))
