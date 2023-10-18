from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("files/", views.select_files, name="select_files"),
]
