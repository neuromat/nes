from django.conf.urls import url
from custom_user import views

urlpatterns = [
    # Reseracher
    url(r'^list/$', views.user_list, name='user_list'),
    url(r'^new/$', views.user_create, name='user_new'),
    url(r'^view/(?P<user_id>\d+)/$', views.user_view, name='user_view'),
    url(r'^edit/(?P<user_id>\d+)/$', views.user_update, name='user_edit'),

    # Institution
    url(r'^institution/new/$', views.institution_create, name='institution_new'),
    url(r'^institution/(?P<institution_id>\d+)/$', views.institution_view, name='institution_view'),
    url(r'^institution/edit/(?P<institution_id>\d+)/$', views.institution_update, name='institution_edit'),
]
