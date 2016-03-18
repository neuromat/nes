from django.conf.urls import patterns, url

urlpatterns = patterns(
    'export.views',

    url(r'^create/$', 'export_create', name='export_create'),
    # url(r'^(?P<survey_id>\d+)/$', 'survey_view', name='survey_view'),
    # url(r'^new/$', 'survey_create', name='survey_create'),
    # url(r'^edit/(?P<survey_id>\d+)/$', 'survey_update', name='survey_edit'),

)
