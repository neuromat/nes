from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'quiz.views.search_patient', name='search_patient'),

    url(r'^patient/new/$', 'quiz.views.patient_create', name='patient_new'),
    url(r'^patient/edit/(?P<patient_id>\d+)/$', 'quiz.views.patient_update', name='patient_edit'),
    url(r'^patient/delete/(?P<patient_id>\d+)/$', 'quiz.views.patient_delete', name='patient_delete'),

    #url(r'^register/$', 'quiz.views.register', name='register'),

    url(r'^search/$', 'quiz.views.search_patients_ajax'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'quiz.views.patient', name='patient_view'),
)


# original
#     '',
#     url(r'^$', 'quiz.views.search_patient', name='search_patient'),
#     url(r'^register/$', 'quiz.views.register', name='register'),
#     url(r'^search/$', 'quiz.views.search_patients_ajax'),
#     url(r'^patient/(?P<patient_id>\d+)/$', 'quiz.views.patient'),
#     """
