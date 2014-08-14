from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^list/$', 'experiment.views.experiment_list', name='experiment_list'),
    url(r'^new/$', 'experiment.views.experiment_create', name='experiment_new'),
    url(r'^edit/(?P<experiment_id>\d+)/$', 'experiment.views.experiment_update', name='experiment_edit'),
    url(r'^(?P<experiment_id>\d+)/subjects/$', 'experiment.views.subjects', name='subjects'),
    url(r'^subject/search/$', 'experiment.views.search_patients_ajax', name='subject_search'),
    url(r'^(?P<experiment_id>\d+)/subjects/(?P<patient_id>\d+)/$',
        'experiment.views.subjects_insert', name='subject_insert'),
    url(r'^(?P<experiment_id>\d+)/subjects/delete/(?P<subject_id>\d+)/$',
        'experiment.views.subjects_delete', name='subject_delete'),
)
