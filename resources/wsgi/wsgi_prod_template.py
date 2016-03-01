# -*- coding: utf-8 -*-

"""
WSGI config for qdc project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
# from django.core.wsgi import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/nes-system/lib/python2.7/site-packages')

paths = ['/var/www', '/var/www/nes-system', '/var/www/nes-system/nes', '/var/www/nes-system/nes/patientregistrationsystem', '/var/www/nes-system/nes/patientregistrationsystem/qdc',]

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")

# Activate virtual env
activate_env=os.path.expanduser("/var/www/nes-system/bin/activate_this.py")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
