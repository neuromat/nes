from django.conf.urls import patterns, url

from quiz import views

urlpatterns = patterns('',
    url(r'^$', views.pg_home, name='pg_home' )
    url(r'^$', views.search_patient)
    hahahaha