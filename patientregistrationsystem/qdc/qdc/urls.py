from django.conf import settings
from django.conf.urls import include, url
from qdc import views as qdcviews
from django.contrib.auth import views as authviews
from django.views.i18n import javascript_catalog
from django.conf.urls.static import static
from .forms import PasswordChangeFormCustomized
from django.contrib import admin
import os
from django.views.static import serve as staticserve

from custom_user.forms import CustomPasswordResetForm

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^patient/', include('patient.urls')),
    url(r'^user/', include('custom_user.urls')),
    url(r'^experiment/', include('experiment.urls')),
    url(r'^survey/', include('survey.urls')),
    url(r'^export/', include('export.urls')),
    url(r'^plugin/', include('plugin.urls')),
    url(r'^home/$', qdcviews.contact, name='contact'),
    url(r'^accounts/login/$', authviews.login, name='login'),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^logout/$', authviews.logout_then_login, {'login_url': '/home'}, name='logout'),
    url(r'^password_change/$', authviews.password_change,
        {'template_name': 'registration/change_password_custom.html',
         'post_change_redirect': 'password_changed',
         'password_change_form': PasswordChangeFormCustomized}, name='password_change'),
    url(r'^password_changed_redirected/$', qdcviews.password_changed, name='password_changed'),
    url(r'^password_change/done/$', authviews.password_change_done, name='password_change_done'),
    url(r'^user/password/reset/$', authviews.password_reset,
        {'post_reset_redirect': '/user/password/reset/done/', 'password_reset_form': CustomPasswordResetForm},
        name="password_reset"),
    url(r'^user/password/reset/done/$',
     authviews.password_reset_done),
    url(r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     authviews.password_reset_confirm,
     {'post_reset_redirect': '/user/password/done/'}),
    url(r'^user/password/done/$',
     authviews.password_reset_complete),
    url(r'^$', qdcviews.contact, name='contact'),
    url(r'^language/change/(?P<language_code>(?:(?:\w{2})|(?:\w{2}\-\w{2})))$', qdcviews.language_change, name='language_change'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^home/check_upgrade/$', qdcviews.check_upgrade, name='check_upgrade'),
    url(r'^home/upgrade_nes/$', qdcviews.upgrade_nes, name='check_upgrade'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# internationalization
js_info_dict = {
    'packages': ('patient', 'experiment', 'survey', 'custom_user', 'quiz', ),
}

urlpatterns += [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript_catalog'),
]

if settings.DEBUG404:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', staticserve,
         {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    ]

handler403 = qdcviews.qdc_permission_denied_view
