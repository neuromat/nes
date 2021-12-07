.. _installation-using-a-docker-container:

####################################
Instalación mediante contenedores Docker
####################################

.. _tutorial-to-install-nes-using-a-single-docker-container:

***************************************************
Tutorial para ejecutar NES con un único contenedor Docker
***************************************************

Es posible preparar un contenedor Docker que incluye todo lo que necesita para usar NES. Este tutorial incluye:

* 'Instalación de Docker'_
* 'Instalación de Docker Toolbox'_
* 'Primera carga de contenedores NES Docker'_
* 'Acceso a NES'_
* 'Acceso a LimeSurvey'_
* 'Uso del contenedor NES Docker después de la primera carga'_
* 'Información útil'_

.. _docker-installation:

===================
Instalación del Docker
===================

Puedes descargar `Docker Community Edition`_ para varios sistemas operativos.

.. note:: Docker para Windows requiere Windows 10 Professional o Windows 10 Enterprise de 64 bits. Para otras versiones (Windows 10 Home, Windows 8 o Windows 7), debe obtener Docker Toolbox.

.. _docker-toolbox-installation:

===========================
Instalación de Docker Toolbox
===========================

Si está utilizando Windows y no tiene los requisitos para instalar Docker para Windows (consulte `Docker installation`_), puede instalar `Docker Toolbox`_

.. note:: En la pantalla de instalación 'Seleccionar componentes', seleccione la opción 'Git para Windows`;

.. note:: En la pantalla de instalación 'Seleccionar tareas adicionales', seleccione la opción 'Instalar VirtualBox con el controlador NDISS (NDIS6 predeterminado)`;

.. note:: Después de la instalación, ejecutando ''Docker Quickstart Terminal'', tal vez Firewall de Windows bloquee la carga de Docker. En este caso, detenga el firewall, cargue ''Docker Quickstart Terminal'' e inicie el firewall nuevamente.

.. _first-nes-docker-container-loading:

==================================
Primera carga de contenedores de NES Docker
==================================

Después de la instalación de Docker (o Docker Toolbox), abra el terminal (o ``Docker Quickstart Terminal`` Si está utilizando Docker Toolbox) y ejecute el comando siguiente para descargar y ejecutar el contenedor NES::

    docker run -it --name nes -p 8080:8080 -p 8000:8000 neuromat/nes

.. note:: Para la persistencia de los datos, es aconsejable el uso de 'Volúmenes'_ que ya se crean en la ejecución del contenedor NES, pero no tendrán referencias mnemotécnicas en comparación con los volúmenes con nombre creados manualmente.

.. note:: Algunas variables de entorno se pueden establecer en la ejecución del contenedor NES para adaptarse a la configuración específica de la instalación. Dichas variables están disponibles en 'REPOSITORIO NES en Docker Hub'_.

.. _accessing-nes:

=============
Accesando NES
=============

Después de cargar el contenedor, puede acceder al sistema NES utilizando el puerto 8000, pero la URL depende de si está utilizando Docker o Docker Toolbox.

Si utiliza Docker (y no Docker Toolbox), puede acceder a NES mediante `localhost` o la IP de su máquina, e.g.::

    http://localhost:8000

Sin embargo, si está utilizando Docker Toolbox, tendrá que conocer la IP que Docker Toolbox designó para esta carga. Para conocer esta IP, ejecute ``Docker Quickstart Terminal`` y obtener la IP que se muestra en la primera línea. Ahora, puede llamar a la URL::

    http://<docker ip>:8000

Después de acceder a la página de inicio de sesión, utilice el usuario `nes_admin` (contraseña `nes_admin_password`).

.. _accessing-limesurvey:

====================
Accesando LimeSurvey
====================

Este contenedor también contiene una instalación de LimeSurvey. Su acceso es desde el puerto 8080 y la URL depende de si está utilizando Docker o Docker Toolbox (consulte `Accessing NES`_)::

    http://localhost:8080/admin

o::

    http://<docker ip>:8080/admin

Después de acceder a la página de inicio de sesión de LimeSurvey, utilice el usuario `limesurvey_admin` (contraseña `limesurvey_admin_password`).

.. _using-nes-docker-container-after-first-loading:

==============================================
Uso del contenedor DOCKER de NES después de la primera carga
==============================================

Después de la primera carga, el contenedor NES ya está descargado e instalado en su máquina. Sin embargo, al reiniciar el equipo, el contenedor se detiene. Luego, para cargarlo nuevamente, es necesario iniciar el contenedor NES usando el siguiente comando::

    docker start nes

.. _useful-information:

==================
Información util
==================

* Para obtener información más detallada, consulte `NES repository on Docker Hub`_
* Acceso a la base de datos de Container NES: usuario `nes_user`, contraseña `nes_password`
* Acceso a la base de datos de Container LimeSurvey: usuario `limesurvey_user`, contraseña `limesurvey_password`

.. _tutorial-to-run-nes-using_docker-compose:

****************************************
Tutorial para ejecutar NES usando Docker Compose
****************************************

Suponiendo que ya ha instalado Docker (consulte `Docker installation`_ y `Docker Toolbox installation`_), también ha instalado Docker Compose, ya que vienen empaquetados juntos y no hay necesidad de configuración adicional.

Este tutorial incluye:

* `Building docker-compose file`_
* `Running the composed NES container`_

.. _building-docker-compose-file:

============================
Creación de archivos docker-compose
============================

Para ejecutar la versión compuesta de NES necesita crear un archivo docker-compose.yml, para ello puede utilizar el siguiente ejemplo:

.. code-block:: yaml

   version: '2'
   services:

     # Postgres_LimeSurvey
     db_limesurvey:
       image: postgres:alpine
       volumes:
         - "limesurvey_pgdata:/var/lib/postgresql/data"
       environment:
         - POSTGRES_PASSWORD=limesurvey_password
         - POSTGRES_DB=limesurvey_db
         - POSTGRES_USER=limesurvey_user

     # LimeSurvey
     limesurvey:
       image: neuromat/nes-compose:limesurvey
       volumes:
         - "limesurvey_data:/var/www/limesurvey"
       environment:
         - LIMESURVEY_PORT=8080
         - LIMESURVEY_DB_TYPE=pgsql
         - LIMESURVEY_DB_HOST=db_limesurvey
         - LIMESURVEY_DB_PORT=5432
         - LIMESURVEY_DB=limesurvey_db
         - LIMESURVEY_DB_TABLE_PREFIX=lime_
         - LIMESURVEY_DB_USER=limesurvey_user
         - LIMESURVEY_DB_PASSWORD=limesurvey_password
         - LIMESURVEY_ADMIN_USER=limesurvey_admin
         - LIMESURVEY_ADMIN_NAME=limesurvey_admin
         - LIMESURVEY_ADMIN_EMAIL=limesurvey@limemail.com
         - LIMESURVEY_ADMIN_PASSWORD=limesurvey_admin_password
         - LIMESURVEY_URL_FORMAT=path
       ports:
         - "8080:8080"
       depends_on:
         - db_limesurvey

     # Postgres_NES
     db_nes:
       image: postgres:alpine
       volumes:
         - "nes_pgdata:/var/lib/postgresql/data"
       environment:
         - POSTGRES_PASSWORD=nes_password
         - POSTGRES_DB=nes_db
         - POSTGRES_USER=nes_user

     # Neuroscience Experiments System
     nes:
       image: neuromat/nes-compose:nes
       volumes:
         - "nes_data:/nes"
       environment:
         - NES_DB_TYPE=pgsql
         - NES_DB_HOST=db_nes
         - NES_DB=nes_db
         - NES_DB_USER=nes_user
         - NES_DB_PASSWORD=nes_password
         - NES_DB_PORT=5432
         - LIMESURVEY_HOST=limesurvey
         - LIMESURVEY_PORT=8080
         - LIMESURVEY_ADMIN_USER=limesurvey_admin
         - LIMESURVEY_ADMIN_PASSWORD=limesurvey_admin_password
         - NES_SECRET_KEY=_my_very_secret_key_
         - NES_IP=0.0.0.0
         - NES_PORT=8000
         - NES_ADMIN_USER=nes_admin
         - NES_ADMIN_EMAIL=nes_admin@nesmail.com
         - NES_ADMIN_PASSWORD=nes_admin_password
       stdin_open: true
       tty: true
       ports:
        - "8000:8000"
       depends_on:
         - db_nes
         - limesurvey

   volumes:
     limesurvey_pgdata:
     nes_pgdata:
     limesurvey_data:
     nes_data:


Puede encontrar más información sobre las variables ambientales y la integración de servicios para la versión compuesta de NES en `NES-compose repository on Docker Hub`_.

.. _running-the-composed-nes-container:

==================================
Ejecución del contenedor NES compuesto
==================================

Después de configurar el archivo docker-compose en `Building docker-compose file`_ Sólo tiene que ejecutar el siguiente comando para tener una versión de contenedor completamente implementada de NES::

    docker-compose up

A partir de este paso, NES y LimeSurvey se comportarán igual que en la configuración de un solo contenedor (consulte `Accessing NES`_ y `Accessing LimeSurvey`_).


**********************
Información adicional
**********************

* Cualquier información adicional sobre Docker o Docker compose se puede encontrar en `docker documentation`_.
* La contenedorización de NES puede encontrar más información, así como cualquier otro proyecto de contenedorización de Neuromat, en `NeuroMat organization on Docker Hub`_.

**********
Referencias
**********
.. target-notes::

.. _`Docker Community Edition`: https://www.docker.com/community-edition
.. _`Docker Toolbox`: https://docs.docker.com/toolbox/overview/
.. _`Volumes`: https://docs.docker.com/storage/volumes/
.. _`NES repository on Docker Hub`: https://hub.docker.com/r/neuromat/nes
.. _`NES-compose repository on Docker Hub`: https://hub.docker.com/r/neuromat/nes-compose
.. _`docker documentation`: https://docs.docker.com/
.. _`NeuroMat organization on Docker Hub`: https://hub.docker.com/r/neuromat/