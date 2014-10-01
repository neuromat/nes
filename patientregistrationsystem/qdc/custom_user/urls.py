from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^search/$', 'custom_user.views.user_list', name='user_list'),
    url(r'^new/$', 'custom_user.views.user_create', name='user_new'),
    url(r'^edit/(?P<user_id>\d+)/$', 'custom_user.views.user_update', name='user_edit'),
)
