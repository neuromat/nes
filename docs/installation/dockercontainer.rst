.. _installation-using-a-docker-container:

Installation using a Docker container
=====================================

.. _tutorial-to-install-nes-using-a-docker-container:

Tutorial to install NES using a Docker container
------------------------------------------------

NeuroMat prepared a Docker container that includes all you need to use NES. This tutorial includes:

* Docker installation
* Docker Toolbox installation
* First NES Docker container loading
* Using NES Docker container after first loading
* Accessing NES
* Accessing LimeSurvey
* Useful information

.. _docker-installation:

Docker installation
```````````````````
Using `this link <https://www.docker.com/community-edition>`_ you can download Docker Community Edition for several operational systems.

.. note:: Docker for Windows requires Windows 10 Professional or Windows 10 Enterprise 64-bit. For other versions (Windows 10 Home, Windows 8, or Windows 7), you must get Docker Toolbox.

.. _docker-toolbox-installation:

Docker Toolbox installation
```````````````````````````
If you are using Windows and do not have the requirements to install Docker for Windows (see the topic `Docker installation`), you can install Docker Toolbox using `this link <https://docs.docker.com/toolbox/overview/>`_

.. note:: In the `Select Components` installation screen, select the option `Git for Windows`;

.. note:: In the `Select Additional Tasks` installation screen, select the option `Install VirtualBox with NDISS driver (default NDIS6)`;

.. note:: After installation, running ``Docker Quickstart Terminal``, maybe Windows Firewall block the Docker loading. In this case, stop the firewall, load ``Docker Quickstart Terminal``, and start the firewall again.

.. _first-nes-docker-container-loading:

First NES Docker container loading
``````````````````````````````````
After Docker (or Docker Toolbox) installation, open the terminal (or ``Docker Quickstart Terminal`` if you are using Docker Toolbox) and run the command below to download and run the NES container::

    docker run -dit --name nes -p 8080:8080 -p 8000:8000 neuromat/nes

.. _accessing-nes:

Accessing NES
`````````````

After load the container, you are able to access the NES system using the port 8087, but the URL depends if you are using Docker or Docker Toolbox.

if you are using Docker (and not Docker Toolbox), you can access NES using `localhost` or the IP of your machine, e.g.::

    http://localhost:8000

However, if you are using Docker Toolbox, you will have to know the IP that the Docker Toolbox designated for this loading. To know this IP, run ``Docker Quickstart Terminal`` and get the IP shown in the first line. Now, you can call the URL::

    http://<docker ip>:8000

After access the login page, use the user `nes_admin` (password `nes_admin_password`).

.. _accessing-limesurvey:

Accessing LimeSurvey
````````````````````

This container also contains a LimeSurvey installation. Its access is from the port 8088 and the URL depends if you are using Docker or Docker Toolbox (see the topic `Accessing NES`_)::

    http://localhost:8080/admin

or::

    http://<docker ip>:8080/admin

After access the LimeSurvey login page, use the user `limesurvey_admin` (password `limesurvey_admin_password`).

.. _using-nes-docker-container-after-first-loading:

Using NES Docker container after first loading
``````````````````````````````````````````````

After the first loading, NES container is already downloaded and installed in your machine. However, when you restart the machine, the container is stopped. Then, to load it again, it is necessary to start the NES container using the following command::

    docker start nes

.. _useful-information:

Useful information
``````````````````

* NeuroMat repository on Docker Hub is located at https://hub.docker.com/r/neuromat/
* Container NES database access: user `nes_user`, password `nes_password`
* Container LimeSurvey database access: user `limesurvey_user`, password `limesurvey_password`
