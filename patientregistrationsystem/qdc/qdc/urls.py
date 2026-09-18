from django.conf import settings
from django.urls import include, re_path, reverse_lazy
from qdc import views as qdcviews
from django.contrib.auth import views as authviews
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.static import static
from .forms import PasswordChangeFormCustomized
from django.contrib import admin
import os
from django.views.static import serve as staticserve

from custom_user.forms import CustomPasswordResetForm

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^patient/', include('patient.urls')),
    re_path(r'^user/', include('custom_user.urls')),
    re_path(r'^experiment/', include('experiment.urls')),
    re_path(r'^survey/', include('survey.urls')),
    re_path(r'^export/', include('export.urls')),
    re_path(r'^plugin/', include('plugin.urls')),
    re_path(r'^home/$', qdcviews.contact, name='contact'),
    re_path(r'^accounts/login/$', authviews.LoginView.as_view(), name='login'),
    re_path(r'^account/', include('django.contrib.auth.urls')),
    # Fase3b: logout_then_login removido no 4.1. LogoutView aceita GET no 4.2 (POST passa a exigir na 5.0).
    re_path(r'^logout/$', authviews.LogoutView.as_view(next_page='/home'), name='logout'),
    re_path(r'^password_change/$', authviews.PasswordChangeView.as_view(
        template_name='registration/change_password_custom.html',
        success_url=reverse_lazy('password_changed'),
        form_class=PasswordChangeFormCustomized), name='password_change'),
    re_path(r'^password_changed_redirected/$', qdcviews.password_changed, name='password_changed'),
    re_path(r'^password_change/done/$', authviews.PasswordChangeDoneView.as_view(), name='password_change_done'),
    re_path(r'^user/password/reset/$', authviews.PasswordResetView.as_view(
        success_url='/user/password/reset/done/', form_class=CustomPasswordResetForm),
        name="password_reset"),
    re_path(r'^user/password/reset/done/$',
     authviews.PasswordResetDoneView.as_view()),
    # Fase3b: uidb36 -> uidb64 (nome esperado pela view moderna). post_reset_redirect -> success_url.
    re_path(r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
     authviews.PasswordResetConfirmView.as_view(
        success_url='/user/password/done/')),
    re_path(r'^user/password/done/$',
     authviews.PasswordResetCompleteView.as_view()),
    re_path(r'^$', qdcviews.contact, name='contact'),
    re_path(r'^language/change/(?P<language_code>(?:(?:\w{2})|(?:\w{2}\-\w{2})))$', qdcviews.language_change, name='language_change'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^home/check_upgrade/$', qdcviews.check_upgrade, name='check_upgrade'),
    re_path(r'^home/upgrade_nes/$', qdcviews.upgrade_nes, name='check_upgrade'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# internationalization
js_info_dict = {
    'packages': ('patient', 'experiment', 'survey', 'custom_user', 'quiz', ),
}

urlpatterns += [
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(**js_info_dict), name='javascript_catalog'),
]

if settings.DEBUG404:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', staticserve,
         {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    ]

handler403 = qdcviews.qdc_permission_denied_view
