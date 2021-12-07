.. _tutorial-to-install-the-latest-version-of-nes:

Tutorial para instalar la versión más reciente de NES
=============================================
En esta guía, demostraremos cómo instalar y configurar NES en un entorno virtual Python. Luego configuraremos PostgreSQL y Apache. 

.. _important-technical-information:

Información técnica importante
-------------------------------
* Esta guía recorre una instalación utilizando paquetes disponibles a través de Debian 9 (nombre en código: Stretch), pero se puede adaptar fácilmente a otros sistemas operativos Unix.
* Se recomienda usar virtualenv para instalar NES. Esto se debe a que cuando se utiliza virtualenv, se crea un entorno aislado con sus propios directorios de instalación.
* La última versión de NES solo funciona con Python 3.
* Para fines de demostración, utilizaremos el `/usr/local` para implementar NES. Este directorio parece ser el lugar correcto según el `Linux Foundation <https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html>`_. 

.. _initial-setup-nes:

Configuración inicial
-------------
1. Antes de seguir los pasos de este tutorial, asegúrese de que todos sus repositorios estén actualizados::

    apt-get update

2. Instalar algunos paquetes::

    apt-get install python-pip git virtualenv graphviz libpq-dev python-dev

    apt-get build-dep python-psycopg2

3. Cree el virtualenv (verifique la versión correcta de Python que está utilizando)::

    cd /usr/local

    virtualenv nes-system -p /usr/bin/python3.5

4. Ejecute lo siguiente para activar este nuevo entorno virtual::

    source nes-system/bin/activate

5. Los próximos pasos se ejecutarán dentro de virtualenv::

    cd nes-system

6. Clone la NES. Compruebe la última versión de TAG `here <https://github.com/neuromat/nes/releases>`_::

    git clone -b TAG-X.X https://github.com/neuromat/nes.git

7. Instalar paquetes de Python adicionales::

    cd nes/patientregistrationsystem/qdc/

    pip install -r requirements.txt

.. _deploying-nes-with-apache-postgresql-and-mod-wsgi:

Implementación de NES con Apache, PostgreSQL y mod_wsgi
--------------------------------------------------
1. Instalar los paquetes::

    apt-get install apache2 libapache2-mod-wsgi-py3 postgresql

2. Crear usuario y base de datos (utilizará este usuario/contraseña/base de datos en el siguiente paso)::

    su - postgres

    createuser nes --pwprompt --encrypted

    createdb nes --owner=nes

    exit

3. Use esto `template <https://github.com/neuromat/nes/blob/master/patientregistrationsystem/qdc/qdc/settings_local_template.py>`_ Para crear un archivo denominado settings_local.py y configurar la base de datos::

    cd /usr/local/nes-system/nes/patientregistrationsystem/qdc

    nano qdc/settings_local.py

Edite la base de datos para utilizar el usuario/contraseña/base de datos creada en el paso anterior::

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'nes',
            'USER': 'nes',
            'PASSWORD': 'your_password',
            'HOST': 'localhost',
        }
    }

4. Crear tablas::

    python manage.py migrate

5. Crear super usuario::

    python manage.py createsuperuser

6. Copiar wsgi_default.py file a wsgi.py file y editar wsgi.py::

    cp wsgi_default.py wsgi.py

    nano qdc/wsgi.py

El archivo debe contener::

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
    site.addsitedir('/usr/local/nes-system/lib/python3.5/site-packages')

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

7. Crear un servidor virtual::

    nano /etc/apache2/sites-available/nes.conf

Después, inserte el siguiente contenido recordando que las rutas de acceso y el NombredeServido proporcionado deben cambiarse de acuerdo con su instalación::

    <VirtualHost *:80>
    	ServerName nes.example.com
    	WSGIProcessGroup nes
    
    	DocumentRoot /usr/local/nes-system/nes/patientregistrationsystem/qdc
    
    	<Directory />
    		Options FollowSymLinks
    		AllowOverride None
    	</Directory>
    
    	Alias /media/ /usr/local/nes-system/nes/patientregistrationsystem/qdc/media/ 
    
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

.. Nota::  note el atributo "application-group=%{GLOBAL}", que por lo general no es necesario. Es importante configurarlo debido a la biblioteca mne, como se explicó. `aquí <https://serverfault.com/questions/514242/non-responsive-apache-mod-wsgi-after-installing-scipy/697251#697251?newreg=0819baeba10e4e92a0f459d4042ea98d>`_.

           anote las líneas con las directivas WSGIProcessGroup y WSGIDaemonProcess. Son importantes para configurar la configuración regional utilizada por las bibliotecas externas, como pydot. Sin estas directivas, los caracteres especiales utilizados por, por ejemplo, pydot, no pueden ser aceptados y se podría lanzar una excepción. Los consejos fueron conseguir `aquí <http://blog.dscpl.com.au/2014/09/setting-lang-and-lcall-when-using.html>`_ y `aquí <http://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIDaemonProcess.html>`_ se explican las configuraciones wsgi_mod. Para configurar correctamente la directiva WSGIDaemonProcess, compruebe la codificación que ejecuta el comando "echo $LANG" en la terminal. A veces, el servidor utiliza el "pt_BR.UTF-8", e.g.

8. Carga de datos iniciales (Ver :ref:`script-for-creating-initial-data` para ver más detalles)::

    chmod +x add_initial_data.py

    python manage.py shell < add_initial_data.py

    python manage.py loaddata load_initial_data.json

9. Administración de archivos estáticos::

    mkdir static

    nano qdc/settings_local.py

10. Edite el ``STATIC_ROOT line``::

     STATIC_ROOT = '/usr/local/nes-system/nes/patientregistrationsystem/qdc/static'

11. Recopile los archivos estáticos en ``STATIC_ROOT``::

     python manage.py collecstatic

12. Crear el directorio multimedia::

     mkdir media

13. Cambiar el propietario de los directorios ``.git`` y `patientregistrationsystem`::

     cd /usr/local/nes-system/nes/

     chown -R www-data .git

     chown -R www-data patientregistrationsystem 

14. Habilitar el host virtual::

     a2ensite nes

     systemctl reload apache2