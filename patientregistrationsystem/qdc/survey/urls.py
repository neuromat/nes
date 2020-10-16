from django.conf.urls import url
from survey import views

urlpatterns = [
    url(r'^list/$', views.survey_list, name='survey_list'),
    url(r'^(?P<survey_id>\d+)/$', views.survey_view, name='survey_view'),
    url(r'^new/$', views.survey_create, name='survey_create'),
    url(r'^edit/(?P<survey_id>\d+)/$', views.survey_update, name='survey_edit'),
    url(r'^edit/(?P<survey_id>\d+)/sensitive_questions/$',
        views.survey_update_sensitive_questions,
        name='survey_edit_sensitive_questions'),
    url(r'^update_acquisitiondate/(?P<survey_id>\d+)',
        views.update_survey_acquisitiondate_view,
        name='update_survey_acquisitiondate')
]
