.. _how-to-install-limesurvey:

Cómo instalar LimeSurvey
=========================

.. _tutorial-to-install-the-latest-version-of-limesurvey:

Tutorial para instalar la última versión de LimeSurvey
----------------------------------------------------

En esta guía, demostraremos cómo instalar y configurar LimeSurvey. Asumiremos que ya tienes un servidor con Apache y PostgreSQL instalado (si instalaste NES, entonces lo tienes!).

.. _important-technical-information:

Información técnica importante
```````````````````````````````
* Esta guía recorre una instalación utilizando paquetes disponibles a través de Debian 9 (nombre en código: Stretch), pero se puede adaptar fácilmente a otros sistemas operativos Unix.
* Para fines de demostración, utilizaremos el directorio ``/var/www`` para implementar LimeSurvey.
* Compruebe siempre el `manual oficial LimeSurvey <https://manual.limesurvey.org/>`_ para obtener la información más actualizada!

.. _initial-setup-limesurvey:

Configuración Inicial
`````````````
1. Antes de seguir los pasos de este tutorial, asegúrese de que todos sus repositorios estén actualizados::

    apt-get update

2. Instale algunos paquetes::

    apt-get install php php-pgsql php-gd php-imap php-mbstring php-ldap php-zip php-xml

3. Compruebe la última versión de LimeSurvey `aquí <https://www.limesurvey.org/stable-release>`_ y descargue el archivo con la extension `tar.gz` . 

4. Extraiga el archivo (cambie el nombre del archivo de acuerdo con lo que ha descargado)::

    tar xzvf limesurvey2_X.X.tar.gz

    rm limesurvey2_X.X.tar.gz

5. Cambiar propietario y grupo::

    chown -R www-data.www-data limesurvey/

6. Cambiar permisos de directorio::

    chmod -R o-rwx limesurvey/

    chmod -R 770 limesurvey/application/config/

    chmod -R 770 limesurvey/upload/

    chmod -R 770 limesurvey/tmp/
 
7. Crear usuario y base de datos (pronto usará este usuario/contraseña/base de datos)::

    su - postgres

    createuser limesurvey --pwprompt --encrypted

    createdb limesurvey --owner=limesurvey

    exit

8. Crear un host virtual::

    nano /etc/apache2/sites-available/limesurvey.conf

Inserte el siguiente contenido, pero recordando que las rutas de acceso y el NombredeServidor proporcionado deben cambiarse según la instalación::

    <VirtualHost *:80>
  	ServerName limesurvey.example.com

    	DocumentRoot /var/www/limesurvey

    	<Directory />
    	    	Options FollowSymLinks
    	    	AllowOverride None
    	</Directory>

    	<Directory /var/www/limesurvey>
    	    	Options Indexes FollowSymLinks MultiViews
    	    	AllowOverride None
    	    	Order allow,deny
    	    	allow from all
    	    	AcceptPathInfo On
    	</Directory>

    	ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/

    	<Directory "/usr/lib/cgi-bin">
    	    	AllowOverride None
    	    	Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
    	    	Order allow,deny
    	    	Allow from all
    	</Directory>

    	ErrorLog ${APACHE_LOG_DIR}/limesurvey_ssl_error.log
    	LogLevel warn
    	CustomLog ${APACHE_LOG_DIR}/limesurvey_ssl_access.log combined
    </VirtualHost>

9. Habilitar el host virtual::

    a2ensite limesurvey

    systemctl reload apache2

10. Configuración basada en web

Usando un navegador, acceda al servidor utilizando la dirección IP de la máquina o su nombre y complete la instalación. En este paso:

* Seleccione el idioma que se utilizará
* Tienes que estar de acuerdo con la licencia
* Vea si tiene todos los paquetes necesarios instalados
* Establecer la base de datos (utilizando las credenciales del paso 7)
* Crear y rellenar la base de datos 
* Crear un usuario administrador
