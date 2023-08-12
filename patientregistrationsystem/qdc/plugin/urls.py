from django.urls import re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from plugin import views

urlpatterns = [
    url(r'^$', views.send_to_plugin, name='send-to-plugin'),
    url(r'^get_participants_by_experiment/(?P<experiment_id>\d+)/$', views.select_participants),
]

urlpatterns += staticfiles_urlpatterns()
