from django.conf.urls import patterns, url

urlpatterns = patterns(
    'export.views',

    url(r'^create/$', 'export_create', name='export_create'),
    url(r'^view/$', 'export_view', name='export_view'),
    # url(r'^result/(?P<return_response>\d+)/(?P<error_message>\d+)$', 'export_result', name='export_result'),
    # url(r'^(?P<survey_id>\d+)/$', 'survey_view', name='survey_view'),
    # url(r'^new/$', 'survey_create', name='survey_create'),
    # url(r'^edit/(?P<survey_id>\d+)/$', 'survey_update', name='survey_edit'),

    url(r'^participants/$', 'participant_selection', name='participant_selection'),

)
