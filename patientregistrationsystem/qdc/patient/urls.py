from django.conf.urls import patterns, url

urlpatterns = patterns(
    'patient.views',

    url(r'^$', 'search_patient', name='search_patient'),
    url(r'^find/$', 'search_patient', name='search_patient'),
    url(r'^advanced_search/$', 'advanced_search', name='advanced_search'),

    url(r'^new/$', 'patient_create', name='patient_new'),
    url(r'^edit/(?P<patient_id>\d+)/$', 'patient_update', name='patient_edit'),
    url(r'^search/$', 'search_patients_ajax', name='patient_search'),
    url(r'^verify_homonym/$', 'patients_verify_homonym', name='patients_verify_homonym'),
    url(r'^verify_homonym_excluded/$', 'patients_verify_homonym_excluded', name='patients_verify_homonym_excluded'),
    url(r'^(?P<patient_id>\d+)/$', 'patient_view', name='patient_view'),
    url(r'^restore/(?P<patient_id>\d+)/$', 'restore_patient', name='patient_restore'),

    # medical_record (create, read, update)
    url(r'^(?P<patient_id>\d+)/medical_record/new/$', 'medical_record_create', name='medical_record_new'),
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/$', 'medical_record_view', name='medical_record_view'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/$', 'medical_record_update',
        name='medical_record_edit'),

    # cid
    url(r'^medical_record/cid-10/$', 'search_cid10_ajax', name='cid10_search'),

    # diagnosis (create, delete, update)
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<medical_record_id>\d+)/diagnosis/(?P<cid10_id>\d+)/$',
        'diagnosis_create', name='diagnosis_create'),
    url(r'^(?P<patient_id>\d+)/medical_record/new/diagnosis/(?P<cid10_id>\d+)/$',
        'medical_record_create_diagnosis_create', name='medical_record_diagnosis_create'),
    url(r'^diagnosis/delete/(?P<patient_id>\d+)/(?P<diagnosis_id>\d+)/$', 'diagnosis_delete', name='diagnosis_delete'),

    # exam (create, read, update, delete)
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/diagnosis/(?P<diagnosis_id>\d+)/exam/new/$',
        'exam_create', name='exam_create'),
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/exam/(?P<exam_id>\d+)/$', 'exam_view',
        name='exam_view'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/edit/(?P<exam_id>\d+)/$', 'exam_edit',
        name='exam_edit'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/remove/(?P<exam_id>\d+)/$', 'exam_delete',
        name='exam_delete'),

    # exam file (delete)
    url(r'^exam_file/delete/(?P<exam_file_id>\d+)/$', 'exam_file_delete', name='exam_file_delete'),

    # questionnaire response
    url(r'^patient_questionnaire_response/(?P<patient_questionnaire_response_id>\d+)/$',
        'patient_questionnaire_response_view', name='patient_questionnaire_response_view'),
    url(r'^(?P<patient_id>\d+)/questionnaire/(?P<survey_id>\d+)/add_response/$',
        'patient_questionnaire_response_create', name='patient_questionnaire_response_create'),
    url(r'^questionnaire_response/edit/(?P<patient_questionnaire_response_id>\d+)/$',
        'patient_questionnaire_response_update', name='patient_questionnaire_response_edit'),

)
