from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from .forms import PasswordChangeFormCustomized
from django.contrib import admin

from custom_user.forms import CustomPasswordResetForm

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^patient/', include('patient.urls')),
    url(r'^user/', include('custom_user.urls')),
    url(r'^experiment/', include('experiment.urls')),
    url(r'^survey/', include('survey.urls')),
    url(r'^export/', include('export.urls')),
    url(r'^home/$', 'qdc.views.contact', name='contact'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/home'}),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change',
        {'template_name': 'registration/change_password_custom.html',
         'post_change_redirect': 'password_changed',
         'password_change_form': PasswordChangeFormCustomized}),
    url(r'^password_changed_redirected/$', 'qdc.views.password_changed', name='password_changed'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done',
        name='password_change_done'),
    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/',
         'password_reset_form': CustomPasswordResetForm},
        name="password_reset"),
    (r'^user/password/reset/done/$',
     'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'django.contrib.auth.views.password_reset_confirm',
     {'post_reset_redirect': '/user/password/done/'}),
    (r'^user/password/done/$',
     'django.contrib.auth.views.password_reset_complete'),
    url(r'^cep/', include('cep.urls')),
    url(r'^$', 'qdc.views.contact', name='contact'),
    url(r'^language/change/(?P<language_code>(?:(?:\w{2})|(?:\w{2}\-\w{2})))$', 'qdc.views.language_change', name='language_change'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^home/check_upgrade/$', 'qdc.views.check_upgrade', name='check_upgrade'),
    url(r'^home/upgrade_nes/$', 'qdc.views.upgrade_nes', name='check_upgrade'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# internationalization
js_info_dict = {
    'packages': ('patient', 'experiment', 'survey', 'custom_user', 'quiz', ),
}

urlpatterns += patterns(
    '', (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

handler403 = 'qdc.views.qdc_permission_denied_view'
