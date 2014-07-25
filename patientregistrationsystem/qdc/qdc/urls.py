from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from forms import PasswordChangeFormCustomized
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'qdc.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^quiz/', include('quiz.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/quiz'}),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change',
        {'template_name': 'registration/change_password_custom.html',
         'post_change_redirect': 'search_patient',
         'password_change_form': PasswordChangeFormCustomized}),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done',
        name='password_change_done'),
    # url(r'^user/password/reset/$', password_reset, {'template_name': 'registration/password_reset_email.html'}),
    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"),
    (r'^user/password/reset/done/$',
     'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'django.contrib.auth.views.password_reset_confirm',
     {'post_reset_redirect': '/user/password/done/'}),
    (r'^user/password/done/$',
     'django.contrib.auth.views.password_reset_complete'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)