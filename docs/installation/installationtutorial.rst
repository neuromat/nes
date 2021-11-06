.. _tutorial-to-install-the-latest-version-of-nes:

Tutorial to install the latest version of NES
=============================================
In this guide, we will demonstrate how to install and configure NES in a Python virtual environment. We'll then set up PostgreSQL and Apache. 

.. _important-technical-information:

Important technical information
-------------------------------
* This guide walks through an installation by using packages available through Debian 10 (code name: Buster), but can easily be adapted to other Unix operating systems.
* Using virtualenv to install NES is recommended. This is because when you use virtualenv, you create an isolated environment with its own installation directories.
* Latest version of NES works only with Python 3.
* For demonstration purposes, we will use the `/usr/local` directory to deploy NES. This directory seems to be the right place according to the `Linux Foundation <https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html>`_. 
* All the installation commands should be run as root.

.. _initial-setup-nes:

Initial setup
-------------
1. Before running through the steps of this tutorial, make sure that all of your repositories are up to date and::

    apt update

2. Install some packages::

    apt install -y python-pip git virtualenv graphviz libpq-dev python-dev

    apt build-dep -y python-psycopg2

3. Create the virtualenv (check the correct python version you are using)::

    cd /usr/local

    virtualenv nes-system -p /usr/bin/python3.7

4. Run the following to activate this new virtual environment::

    source nes-system/bin/activate

5. Next steps will be executed inside virtualenv::

    cd nes-system

6. Clone the NES. Check the latest TAG version `here <https://github.com/neuromat/nes/tags>`_::

    git clone -b TAG-X.X https://github.com/neuromat/nes.git

7. Install required python packages in your virtual environment::

    cd nes/patientregistrationsystem/qdc/

    pip install -r requirements.txt

.. _deploying-nes-with-apache-postgresql-and-mod-wsgi:

Deploying NES with Apache, PostgreSQL and mod_wsgi
--------------------------------------------------
1. Install the packages::

    apt install -y apache2 libapache2-mod-wsgi-py3 postgresql-11
   
.. Note::
  The latest version of LimeSurvey that works with NES is 2.73.1, and LimeSurvey 2.73.1 only works with PostgreSQL 11 or older versions.  
  So, if NES will be used with LimeSurvey and they will share the same PostgreSQL server, then ``postgresql-11`` is required. But if this is not the case, then ``postgresql-11`` can be replaced by ``postgresql`` in the command above (to install the most recent PostgreSQL version available in Debian).
   
  Check :ref:`how-to-install-limesurvey`.

2. Create user and database (you will use this user/password/database in the next step)::

    service apache2 start
    service postgresql start

    su - postgres

    createuser nes --pwprompt --encrypted

    createdb nes --owner=nes

    exit

3. Use this `template <https://github.com/neuromat/nes/blob/master/patientregistrationsystem/qdc/qdc/settings_local_template.py>`_ to create a file called settings_local.py and configure the database::

    cd /usr/local/nes-system/nes/patientregistrationsystem/qdc

    cp -i qdc/settings_local_template.py qdc/settings_local.py

    nano qdc/settings_local.py

Edit the database to use the user/password/database created in the previous step::

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'nes',
            'USER': 'nes',
            'PASSWORD': 'YOUR PASSWORD HERE',
            'HOST': 'localhost',
        }
    }

Edit the ALLOWED_HOSTS to include the host/domain name (for example, `'nes.example.com'` or `'localhost'`)::

    ALLOWED_HOSTS = ['nes.example.com']

4. Create tables::

    python manage.py migrate
    
    python manage.py createcachetable

5. Create superuser (the administrator of NES)::

    python manage.py createsuperuser

6. Copy wsgi_default.py file to wsgi.py file and edit wsgi.py::

    cp qdc/wsgi_default.py qdc/wsgi.py

    nano qdc/wsgi.py

The file must contain::

    # -*- coding: utf-8 -*-

    """
    WSGI config for qdc project.
    It exposes the WSGI callable as a module-level variable named ``application``.
    For more information on this file, see
    https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
    """
    import os
    import sys
    import site

    # Add the site-packages of the chosen virtualenv to work with
    site.addsitedir('/usr/local/nes-system/lib/python3.7/site-packages')

    # Add the paths according to your installation
    paths = ['/usr/local', '/usr/local/nes-system', '/usr/local/nes-system/nes', '/usr/local/nes-system/nes/patientregistrationsystem', '/usr/local/nes-system/nes/patientregistrationsystem/qdc',]

    for path in paths:
        if path not in sys.path:
            sys.path.append(path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")

    # Activate virtual env
    activate_env=os.path.expanduser("/usr/local/nes-system/bin/activate_this.py")

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

7. Create a virtual host::

    nano /etc/apache2/sites-available/nes.conf

After, insert the following content remembering that the paths and the ServerName provided should be changed according to your installation::

    <VirtualHost *:80>
    	ServerName nes.example.com
    	WSGIProcessGroup nes
    
    	DocumentRoot /usr/local/nes-system/nes/patientregistrationsystem/qdc
    
    	<Directory />
    		Options FollowSymLinks
    		AllowOverride None
    	</Directory>
    
        Alias /media/ /usr/local/nes-system/nes/patientregistrationsystem/qdc/media/ 
        Alias /static/ /usr/local/nes-system/nes/patientregistrationsystem/qdc/static/ 
    
    	<Directory "/usr/local/nes-system/nes/patientregistrationsystem/qdc">
    		Require all granted
    	</Directory>
    
    	WSGIScriptAlias / /usr/local/nes-system/nes/patientregistrationsystem/qdc/qdc/wsgi.py application-group=%{GLOBAL}
    	WSGIDaemonProcess nes lang='en_US.UTF-8' locale='en_US.UTF-8'

    	Alias /img/ /usr/local/nes-system/nes/patientregistrationsystem/qdc/img/ 
    
    	ErrorLog ${APACHE_LOG_DIR}/nes_ssl_error.log
    	LogLevel warn
    	CustomLog ${APACHE_LOG_DIR}/nes_ssl_access.log combined
    </VirtualHost>

.. Note::  note the attribute "application-group=%{GLOBAL}", which is usually not required. It is important to configure it because of the mne library, as explained `here <https://serverfault.com/questions/514242/non-responsive-apache-mod-wsgi-after-installing-scipy/697251#697251?newreg=0819baeba10e4e92a0f459d4042ea98d>`_.

           note the lines with the WSGIProcessGroup and WSGIDaemonProcess directives.They are important to configure the locale used by external libraries, as pydot. Without these directives, special characteres used by, for example, pydot, can not be accepted and an exception could be thrown. The tips were get `here <http://blog.dscpl.com.au/2014/09/setting-lang-and-lcall-when-using.html>`_ and `here <http://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIDaemonProcess.html>`_ the wsgi_mod configurations are explained. To configure the WSGIDaemonProcess directive properly, check the encode running the command "echo $LANG" in the terminal. Sometimes the server uses the "pt_BR.UTF-8", e.g.

8. Loading initial data (Look at :ref:`script-for-creating-initial-data` to see more details)::

    chmod +x add_initial_data.py

    python manage.py shell < add_initial_data.py

    python manage.py loaddata load_initial_data.json

9. Managing static files::

    mkdir static

    nano qdc/settings_local.py

10. Edit the ``STATIC_ROOT line``::

     STATIC_ROOT = '/usr/local/nes-system/nes/patientregistrationsystem/qdc/static'

11. Collects the static files into ``STATIC_ROOT``::

     python manage.py collectstatic

12. Create the media directory::

     mkdir media

13. For Online updates, change the owner of the directories ``.git`` and ``patientregistrationsystem``::

     cd /usr/local/nes-system/nes/
    
     chown -R www-data .git

     chown -R www-data patientregistrationsystem

14. Enable the virtual host::

     a2ensite nes
    
     service apache2 reload
