from django.urls import re_path
from export import views

urlpatterns = [
    url(r'^$', views.export_menu, name='export_menu'),
    url(r'^create/$', views.export_create, name='export_create'),
    url(r'^view/$', views.export_view, name='export_view'),

    url(r'^filter_participants/$', views.filter_participants, name='filter_participants'),
    url(r'^experiment_selection/$', views.experiment_selection, name='experiment_selection'),

    # export (ajax)
    url(r'^get_locations/$', views.search_locations, name='search_locations'),
    url(r'^get_diagnoses/$', views.search_diagnoses, name='search_diagnoses'),
    url(r'^get_experiments_by_study/(?P<study_id>\d+)/$', views.select_experiments_by_study),
    url(r'^get_groups_by_experiment/(?P<experiment_id>\d+)/$', views.select_groups_by_experiment),
]
