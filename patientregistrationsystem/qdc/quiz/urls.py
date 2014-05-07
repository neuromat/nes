from django.conf.urls import patterns, url
from quiz import views


urlpatterns = patterns('',
    url(r'^$', 'quiz.views.pg_home', name='pg_home'),
    url(r'^search/$', 'quiz.views.search_patients'),
    url(r'^patient/(?P<patient_id>\d+)/$', 'quiz.views.patient'),
)
