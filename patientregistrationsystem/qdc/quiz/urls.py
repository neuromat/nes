from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    #url(r'^$', 'quiz.views.search_patient', name='search_patient'),
    url(r'^$', 'quiz.views.contact', name='contact'),
    url(r'^busca/$', 'quiz.views.search_patient', name='search_patient'),
    url(r'^contato/$', 'quiz.views.contact', name='contato'),
    url(r'^busca_avancada/$', 'quiz.views.advanced_search', name='advanced_search'),

    url(r'^patient/new/$', 'quiz.views.patient_create', name='patient_new'),
    url(r'^patient/edit/(?P<patient_id>\d+)/$', 'quiz.views.patient_update', name='patient_edit'),
    url(r'^patient/search/$', 'quiz.views.search_patients_ajax', name='patient_search'),
    url(r'^patient/verify_homonym/$', 'quiz.views.patients_verify_homonym', name='patients_verify_homonym'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'quiz.views.patient', name='patient_view'),
    url(r'^restore/patient/(?P<patient_id>\d+)/$', 'quiz.views.restore_patient', name='patient_restore'),

    url(r'^user/search/$', 'quiz.views.user_list', name='user_list'),
    url(r'^user/new/$', 'quiz.views.user_create', name='user_new'),
    url(r'^user/edit/(?P<user_id>\d+)/$', 'quiz.views.user_update', name='user_edit'),
    url(r'^user/delete/(?P<user_id>\d+)/$', 'quiz.views.user_delete', name='user_delete'),

    url(r'^patient/(?P<patient_id>\d+)/medical_record/new/$', 'quiz.views.medical_record_create',
        name='medical_record_new'),
    url(r'^patient/(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/$', 'quiz.views.medical_record_view',
        name='medical_record_view'),
    url(r'^patient/medical_record/cid-10/$', 'quiz.views.search_cid10_ajax', name='cid10_search'),
    url(r'^patient/(?P<patient_id>\d+)/medical_record/(?P<medical_record_id>\d+)/diagnosis/(?P<cid10_id>\d+)/$',
        'quiz.views.diagnosis_create'),

)