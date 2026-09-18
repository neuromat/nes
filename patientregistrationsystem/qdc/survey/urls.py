from django.urls import re_path
from survey import views

urlpatterns = [
    re_path(r'^list/$', views.survey_list, name='survey_list'),
    re_path(r'^(?P<survey_id>\d+)/$', views.survey_view, name='survey_view'),
    re_path(r'^new/$', views.survey_create, name='survey_create'),
    re_path(r'^edit/(?P<survey_id>\d+)/$', views.survey_update, name='survey_edit'),
    re_path(r'^edit/(?P<survey_id>\d+)/sensitive_questions/$',
        views.survey_update_sensitive_questions,
        name='survey_edit_sensitive_questions'),
    re_path(r'^update_acquisitiondate/(?P<survey_id>\d+)',
        views.update_survey_acquisitiondate_view,
        name='update_survey_acquisitiondate')
]
