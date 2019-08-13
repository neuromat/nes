from django.conf.urls import url
from plugin import views

urlpatterns = [
    url(r'^$', views.send_to_plugin, name='send-to-plugin'),
    url(r'^call_plugin/(?P<user_id>\d+)/(?P<export_id>\d+)/$', views.call_plugin, name='call-plugin')
]
