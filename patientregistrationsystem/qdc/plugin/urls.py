from django.conf.urls import url
from plugin import views

urlpatterns = [
    url(r'^$', views.send_to_plugin, name='send-to-plugin'),
    url(r'^get_participants_by_experiment/(?P<experiment_id>\d+)/$', views.select_participants),
]
