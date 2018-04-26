from django.conf.urls import patterns, url

urlpatterns = patterns(
    'team.views',

    url(r'^registers/$', 'registers', name='registers'),

    # register person
    url(r'^person/list/$', 'person_list', name='person_list'),
    url(r'^person/new/$', 'person_create', name='person_new'),
    url(r'^person/(?P<person_id>\d+)/$', 'person_view', name='person_view'),
    url(r'^person/edit/(?P<person_id>\d+)/$', 'person_update', name='person_edit'),

    # register person (ajax)
    url(r'^person/get_user_attributes/(?P<user_id>\d+)/$', 'get_json_user_attributes'),

    # register institution
    url(r'^institution/list/$', 'institution_list', name='institution_list'),
    url(r'^institution/new/$', 'institution_create', name='institution_new'),
    url(r'^institution/(?P<institution_id>\d+)/$', 'institution_view', name='institution_view'),
    url(r'^institution/edit/(?P<institution_id>\d+)/$', 'institution_update', name='institution_edit'),
)
