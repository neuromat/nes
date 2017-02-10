from django.conf.urls import patterns, url

urlpatterns = patterns(
    'export.views',
    url(r'^$', 'export_menu', name='export_menu'),
    url(r'^create/$', 'export_create', name='export_create'),
    url(r'^view/$', 'export_view', name='export_view'),
    # url(r'^result/(?P<return_response>\d+)/(?P<error_message>\d+)$', 'export_result', name='export_result'),
    # url(r'^(?P<survey_id>\d+)/$', 'survey_view', name='survey_view'),
    # url(r'^new/$', 'survey_create', name='survey_create'),
    # url(r'^edit/(?P<survey_id>\d+)/$', 'survey_update', name='survey_edit'),

    url(r'^filter_participants/$', 'filter_participants', name='filter_participants'),
    # url(r'^export/$', 'export_menu', name='export_menu'),
    url(r'^experiment_selection/$', 'experiment_selection', name='experiment_selection'),

# export (ajax)
#     url(r'^get_experiment_by_study/(?P<study_list>[\w-]+)/$','get_json_experiment_by_study'),
#     url(r'^get_group_by_experiment/(?P<experiment_id>\d+)/$','get_json_group_by_experiment'),

)
