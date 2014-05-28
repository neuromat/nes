from django.conf.urls import patterns, url
from quiz import views


urlpatterns = patterns('',
    url(r'^$', 'quiz.views.search_patient', name='search_patient'),
    url(r'^register/$', 'quiz.views.register', name='register'),
    url(r'^search/$', 'quiz.views.search_patients_ajax'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'quiz.views.patient'),
)
