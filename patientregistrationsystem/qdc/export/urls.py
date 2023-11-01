from django.urls import re_path

from .views import (
    experiment_selection,
    export_create,
    export_menu,
    export_view,
    filter_participants,
    search_diagnosis,
    search_locations,
    select_groups_by_experiment,
    select_experiments_by_study,
)

urlpatterns = [
    re_path(r"^$", export_menu, name="export_menu"),
    re_path(r"^create/$", export_create, name="export_create"),
    re_path(r"^view/$", export_view, name="export_view"),
    re_path(r"^filter_participants/$", filter_participants, name="filter_participants"),
    re_path(
        r"^experiment_selection/$", experiment_selection, name="experiment_selection"
    ),
    # export (ajax)
    re_path(r"^get_locations/$", search_locations, name="search_locations"),
    re_path(r"^get_diagnosis/$", search_diagnosis, name="search_diagnosis"),
    re_path(
        r"^get_experiments_by_study/(?P<study_id>\d+)/$",
        select_experiments_by_study,
    ),
    re_path(
        r"^get_groups_by_experiment/(?P<experiment_id>\d+)/$",
        select_groups_by_experiment,
    ),
]
