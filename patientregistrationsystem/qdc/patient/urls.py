from django.urls import re_path
from patient import views

urlpatterns = [
    re_path(r"^$", views.search_patient, name="search_patient"),
    re_path(r"^find/$", views.search_patient, name="search_patient"),
    re_path(r"^advanced_search/$", views.advanced_search, name="advanced_search"),
    re_path(r"^new/$", views.patient_create, name="patient_new"),
    re_path(r"^edit/(?P<patient_id>\d+)/$", views.patient_update, name="patient_edit"),
    re_path(r"^search/$", views.search_patients_ajax, name="patient_search"),
    re_path(
        r"^verify_homonym/$",
        views.patients_verify_homonym,
        name="patients_verify_homonym",
    ),
    re_path(
        r"^verify_homonym_excluded/$",
        views.patients_verify_homonym_excluded,
        name="patients_verify_homonym_excluded",
    ),
    re_path(r"^(?P<patient_id>\d+)/$", views.patient_view, name="patient_view"),
    re_path(
        r"^restore/(?P<patient_id>\d+)/$", views.restore_patient, name="patient_restore"
    ),
    # medical_record (create, read, update)
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/new/$",
        views.medical_record_create,
        name="medical_record_new",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/$",
        views.medical_record_view,
        name="medical_record_view",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/$",
        views.medical_record_update,
        name="medical_record_edit",
    ),
    # cid
    re_path(r"^medical_record/cid-10/$", views.search_cid10_ajax, name="cid10_search"),
    # diagnosis (create, delete, update)
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/(?P<medical_record_id>\d+)/diagnosis/(?P<cid10_id>\d+)/$",
        views.diagnosis_create,
        name="diagnosis_create",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/new/diagnosis/(?P<cid10_id>\d+)/$",
        views.medical_record_create_diagnosis_create,
        name="medical_record_diagnosis_create",
    ),
    re_path(
        r"^diagnosis/delete/(?P<patient_id>\d+)/(?P<diagnosis_id>\d+)/$",
        views.diagnosis_delete,
        name="diagnosis_delete",
    ),
    # exam (create, read, update, delete)
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/diagnosis/(?P<diagnosis_id>\d+)/exam/new/$",
        views.exam_create,
        name="exam_create",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/(?P<record_id>\d+)/exam/(?P<exam_id>\d+)/$",
        views.exam_view,
        name="exam_view",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/edit/(?P<exam_id>\d+)/$",
        views.exam_edit,
        name="exam_edit",
    ),
    re_path(
        r"^(?P<patient_id>\d+)/medical_record/edit/(?P<record_id>\d+)/exam/remove/(?P<exam_id>\d+)/$",
        views.exam_delete,
        name="exam_delete",
    ),
    # exam file (delete)
    re_path(
        r"^exam_file/delete/(?P<exam_file_id>\d+)/$",
        views.exam_file_delete,
        name="exam_file_delete",
    ),
    # questionnaire response
    re_path(
        r"^(?P<patient_id>\d+)/questionnaire/(?P<survey_id>\d+)/add_response/$",
        views.questionnaire_response_create,
        name="questionnaire_response_create",
    ),
    re_path(
        r"^questionnaire_response/(?P<questionnaire_response_id>\d+)/$",
        views.questionnaire_response_view,
        name="questionnaire_response_view",
    ),
    re_path(
        r"^questionnaire_response/edit/(?P<questionnaire_response_id>\d+)/$",
        views.questionnaire_response_update,
        name="questionnaire_response_edit",
    ),
]
