from django.urls import re_path
from export import views

urlpatterns = [
    re_path(r'^$', views.export_menu, name='export_menu'),
    re_path(r'^create/$', views.export_create, name='export_create'),
    re_path(r'^view/$', views.export_view, name='export_view'),

    re_path(r'^filter_participants/$', views.filter_participants, name='filter_participants'),
    re_path(r'^experiment_selection/$', views.experiment_selection, name='experiment_selection'),

    # export (ajax)
    re_path(r'^get_locations/$', views.search_locations, name='search_locations'),
    re_path(r'^get_diagnoses/$', views.search_diagnoses, name='search_diagnoses'),
    re_path(r'^get_experiments_by_study/(?P<study_id>\d+)/$', views.select_experiments_by_study),
    re_path(r'^get_groups_by_experiment/(?P<experiment_id>\d+)/$', views.select_groups_by_experiment),
]
