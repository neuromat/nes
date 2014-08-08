from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^list/$', 'experiment.views.experiment_list', name='experiment_list'),
)
