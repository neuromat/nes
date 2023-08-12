from django.urls import re_path
from custom_user import views

urlpatterns = [
    # Reseracher
    re_path(r'^list/$', views.user_list, name='user_list'),
    re_path(r'^new/$', views.user_create, name='user_new'),
    re_path(r'^view/(?P<user_id>\d+)/$', views.user_view, name='user_view'),
    re_path(r'^edit/(?P<user_id>\d+)/$', views.user_update, name='user_edit'),

    # Institution
    re_path(r'^institution/new/$', views.institution_create, name='institution_new'),
    re_path(r'^institution/(?P<institution_id>\d+)/$', views.institution_view, name='institution_view'),
    re_path(r'^institution/edit/(?P<institution_id>\d+)/$', views.institution_update, name='institution_edit'),
]
