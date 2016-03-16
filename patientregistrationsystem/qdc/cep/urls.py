# -*- coding: utf-8 -*-
try:
    from django.conf.urls import patterns, url
except ImportError:  # deprecated since Django 1.4
    from django.conf.urls.defaults import patterns, url

from .views import addressGet

urlpatterns = patterns('',
                       url(r'^(?P<zipcode>[\w-]+)/$', addressGet, name='address'),
                       )
