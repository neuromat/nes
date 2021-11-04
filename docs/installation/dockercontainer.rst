.. _installation-using-a-docker-container:

####################################
Installation using Docker containers
####################################

.. _tutorial-to-install-nes-using-a-single-docker-container:

***************************************************
Tutorial to run NES using a single Docker container
***************************************************

NeuroMat prepared a Docker container that includes all you need to use NES. This tutorial includes:

* `Docker installation`_
* `Docker Toolbox installation`_
* `First NES Docker container loading`_
* `Accessing NES`_
* `Accessing LimeSurvey`_
* `Using NES Docker container after first loading`_
* `Useful information`_

.. _docker-installation:

===================
Docker installation
===================

You can download `Docker Community Edition`_ for several operational systems.

.. note:: Docker for Windows requires Windows 10 Professional or Windows 10 Enterprise 64-bit. For other versions (Windows 10 Home, Windows 8, or Windows 7), you must get Docker Toolbox.

.. _docker-toolbox-installation:

===========================
Docker Toolbox installation
===========================

If you are using Windows and do not have the requirements to install Docker for Windows (see `Docker installation`_), you can install `Docker Toolbox`_

.. note:: In the `Select Components` installation screen, select the option `Git for Windows`;

.. note:: In the `Select Additional Tasks` installation screen, select the option `Install VirtualBox with NDISS driver (default NDIS6)`;

.. note:: After installation, running ``Docker Quickstart Terminal``, maybe Windows Firewall block the Docker loading. In this case, stop the firewall, load ``Docker Quickstart Terminal``, and start the firewall again.

.. _first-nes-docker-container-loading:

==================================
First NES Docker container loading
==================================

After Docker (or Docker Toolbox) installation, open the terminal (or ``Docker Quickstart Terminal`` if you are using Docker Toolbox) and run the command below to download and run the NES container::

    docker run -it --name nes -p 8080:8080 -p 8000:8000 neuromat/nes

.. note:: For data persistence it its advisable the use of `Volumes`_ which are already created on NES container execution, but won't have mnemonic references compared to manually created named volumes.

.. note:: Some environment variables may be set at NES container execution to adapt to your setup specific configuration. Such variables are available at `NES repository on Docker Hub`_.

.. _accessing-nes:

=============
Accessing NES
=============

After load the container, you are able to access the NES system using the port 8000, but the URL depends if you are using Docker or Docker Toolbox.

if you are using Docker (and not Docker Toolbox), you can access NES using `localhost` or the IP of your machine, e.g.::

    http://localhost:8000

However, if you are using Docker Toolbox, you will have to know the IP that the Docker Toolbox designated for this loading. To know this IP, run ``Docker Quickstart Terminal`` and get the IP shown in the first line. Now, you can call the URL::

    http://<docker ip>:8000

After access the login page, use the user `nes_admin` (password `nes_admin_password`).

.. _accessing-limesurvey:

====================
Accessing LimeSurvey
====================

This container also contains a LimeSurvey installation. Its access is from the port 8080 and the URL depends if you are using Docker or Docker Toolbox (see `Accessing NES`_)::

    http://localhost:8080/admin

or::

    http://<docker ip>:8080/admin

After access the LimeSurvey login page, use the user `limesurvey_admin` (password `limesurvey_admin_password`).

.. _using-nes-docker-container-after-first-loading:

==============================================
Using NES Docker container after first loading
==============================================

After the first loading, NES container is already downloaded and installed in your machine. However, when you restart the machine, the container is stopped. Then, to load it again, it is necessary to start the NES container using the following command::

    docker start nes

.. _useful-information:

==================
Useful information
==================

* For more detailed information see `NES repository on Docker Hub`_
* Container NES database access: user `nes_user`, password `nes_password`
* Container LimeSurvey database access: user `limesurvey_user`, password `limesurvey_password`

.. _tutorial-to-run-nes-using_docker-compose:

****************************************
Tutorial to run NES using Docker Compose
****************************************

Assuming you have already installed Docker (see `Docker installation`_ and `Docker Toolbox installation`_), you have already installed Docker Compose aswell, since they come packed together and there is no need for extra configuration.

This tutorial includes:

* `Building docker-compose file`_
* `Running the composed NES container`_

.. _building-docker-compose-file:

============================
Building docker-compose file
============================

In order to run the composed version of NES you need to build a docker-compose.yml file, for such you may use the following example:

.. code-block:: yaml

   version: '2'
   services:

     # Postgres_LimeSurvey
     db_limesurvey:
       image: postgres:11-alpine
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

Please note that PostgreSQL version used for LimeSurvey is fixed as `postgres:11-alpine` because the latest version of LimeSurvey that works with NES is 2.73.1 and this version does not work with PostgreSQL12+.

More information regarding environmennt variables and service itegration for the composed version of NES can be found in `NES-compose repository on Docker Hub`_.

.. _running-the-composed-nes-container:

==================================
Running the composed NES container
==================================

After setting up the docker-compose file in `Building docker-compose file`_ you just need to run the following command to have a fully deployed container version of NES::

    docker-compose up

From this step onward, NES and LimeSurvey acess will behave the same as in the single container setup (see `Accessing NES`_ and `Accessing LimeSurvey`_).


**********************
Additional information
**********************

* Any additional information regarding Docker or Docker compose can be found in `docker documentation`_.
* NES containerization further info, aswell as any other Neuromat's containerization project, may be found on `NeuroMat organization on Docker Hub`_.

**********
References
**********
.. target-notes::

.. _`Docker Community Edition`: https://www.docker.com/community-edition
.. _`Docker Toolbox`: https://docs.docker.com/toolbox/overview/
.. _`Volumes`: https://docs.docker.com/storage/volumes/
.. _`NES repository on Docker Hub`: https://hub.docker.com/r/neuromat/nes
.. _`NES-compose repository on Docker Hub`: https://hub.docker.com/r/neuromat/nes-compose
.. _`docker documentation`: https://docs.docker.com/
.. _`NeuroMat organization on Docker Hub`: https://hub.docker.com/r/neuromat/
