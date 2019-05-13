from django.conf.urls import url
from plugin import views

urlpatterns = [
    url(r'^$', views.send_to_plugin, name='send_to_plugin'),
]
