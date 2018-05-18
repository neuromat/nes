from django.conf.urls import patterns, url

urlpatterns = patterns(
    'custom_user.views',
    url(r'^search/$', 'user_list', name='user_list'),
    url(r'^new/$', 'user_create', name='user_new'),
    url(r'^view/(?P<user_id>\d+)/$', 'user_view', name='user_view'),
    url(r'^edit/(?P<user_id>\d+)/$', 'user_update', name='user_edit'),
)
