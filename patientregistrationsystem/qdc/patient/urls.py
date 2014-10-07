from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^find/$', 'patient.views.search_patient', name='search_patient'),
    url(r'^advanced_search/$', 'patient.views.advanced_search', name='advanced_search'),

    url(r'^new/$', 'patient.views.patient_create', name='patient_new'),
    url(r'^edit/(?P<patient_id>\d+)/$', 'patient.views.patient_update', name='patient_edit'),
    url(r'^search/$', 'patient.views.search_patients_ajax', name='patient_search'),
    url(r'^verify_homonym/$', 'patient.views.patients_verify_homonym', name='patients_verify_homonym'),
    url(r'^(?P<patient_id>\d+)/$', 'patient.views.patient', name='patient_view'),
    url(r'^restore/patient/(?P<patient_id>\d+)/$', 'patient.views.restore_patient', name='patient_restore'),

    # medical_record (create, read, update)
    url(r'^(?P<patient_id>\d+)/medical_record/new/$',
        'patient.views.medical_record_create', name='medical_record_new'),
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/$',
        'patient.views.medical_record_view', name='medical_record_view'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/$',
        'patient.views.medical_record_update', name='medical_record_edit'),

    # cid
    url(r'^medical_record/cid-10/$', 'patient.views.search_cid10_ajax', name='cid10_search'),

    # diagnosis (create, delete, update)
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<medical_record_id>\d+)/diagnosis/(?P<cid10_id>\d+)/$',
        'patient.views.diagnosis_create', name='diagnosis_create'),
    url(r'^(?P<patient_id>\d+)/medical_record/new/diagnosis/(?P<cid10_id>\d+)/$',
        'patient.views.medical_record_create_diagnosis_create', name='medical_record_diagnosis_create'),
    url(r'^diagnosis/delete/(?P<patient_id>\d+)/(?P<diagnosis_id>\d+)/$',
        'patient.views.diagnosis_delete', name='diagnosis_delete'),

    # exam (create, read, update, delete)
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/diagnosis/(?P<diagnosis_id>\d+)/exam/new/$',
        'patient.views.exam_create', name='exam_create'),
    url(r'^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/exam/(?P<exam_id>\d+)/$',
        'patient.views.exam_view', name='exam_view'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/edit/(?P<exam_id>\d+)/$',
        'patient.views.exam_edit', name='exam_edit'),
    url(r'^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/remove/(?P<exam_id>\d+)/$',
        'patient.views.exam_delete', name='exam_delete'),

    # exam file (delete)
    url(r'^exam_file/delete/(?P<exam_file_id>\d+)/$',
        'patient.views.exam_file_delete', name='exam_file_delete'),
)
