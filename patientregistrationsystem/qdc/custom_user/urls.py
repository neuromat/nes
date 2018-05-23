from django.conf.urls import patterns, url

urlpatterns = patterns(
    'custom_user.views',

    # Reseracher
    url(r'^list/$', 'user_list', name='user_list'),
    url(r'^new/$', 'user_create', name='user_new'),
    url(r'^view/(?P<user_id>\d+)/$', 'user_view', name='user_view'),
    url(r'^edit/(?P<user_id>\d+)/$', 'user_update', name='user_edit'),

    # Institution
    url(r'^institution/new/$', 'institution_create', name='institution_new'),
    url(r'^institution/(?P<institution_id>\d+)/$', 'institution_view', name='institution_view'),
    url(r'^institution/edit/(?P<institution_id>\d+)/$', 'institution_update', name='institution_edit'),
)
