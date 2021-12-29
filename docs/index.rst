.. Documentacion NES documentation master file, created by
   sphinx-quickstart on Fri Sep 24 11:53:54 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. qdc documentation master file, created by
   sphinx-quickstart on Fri May 18 13:06:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Neuroscience Experiments System (NES)
==============================================
* Neuroscience Experiments System* (NES), un software diseñado para gestionar datos de experimentos de neurociencia. NES proporciona recursos para registrar datos y metadatos de cada paso de un experimento de neurociencia en una plataforma segura y fácil de usar. Fue desarrollado para ayudar a los investigadores en su rutina de recolección de datos a lo largo de un experimento de neurociencia, integrando registros de datos de diferentes tipos, como clínicos, electrofisiológicos, de imágenes y de comportamiento. Además, proporciona un repositorio unificado (base de datos) para los datos experimentales de todo un laboratorio, grupo o proyecto de investigación. Su interfaz web y su formato modular proponen un uso intuitivo de las funcionalidades de gestión de datos. Su uso no depende de ningún conocimiento específico sobre informática.

Caracteristicas
--------
- NES permite registrar el protocolo experimental en formato textual.
- Es posible almacenar varios tipos de datos y metadatos del experimento en cada paso del protocolo experimental.
- La base de datos de NES no es de uso público. NES se instala en una máquina informática de laboratorio que es controlada y gestionada por el mismo laboratorio.
- NES permite exportar todos los datos y metadatos de los experimentos que almacena. 
- Cualquier experimento registrado en NES podría eventualmente ser enviado una base de datos abierta para ser puesto a disposición del público.

Integración con base de datos abierta
-------------------------------------------
Los recursos de NES pueden enviar datos de experimentos a una base de datos abierta, donde los experimentos podrían eventualmente ser puestos a disposición del público.
A través de NES, un investigador podrá enviar los datos y metadatos de sus experimentos a una Base de Datos Abierta.  
Los datos se anonimizan antes de ser enviados desde NES a una base de datos; ningún dato confidencial sale de NES ni se almacena en la base de datos . Cuando un nuevo conjunto de datos de un experimento llega a la Base de Datos , será evaluado por un comité curatorial. El comité analizará si el conjunto de datos es apropiado para su publicación en la base de datos. El investigador será notificado del estado de su envío de datos.
Los investigadores que no tienen instalación de NES pueden enviar los datos y metadatos de sus experimentos a la base de datos.

.. :ref:`how-to-send-experiment-data-from-nes`

Documentación
-------------
El equipo de desarrollo de software trabaja continuamente en el desarrollo del Sistema de Experimentos de Neurociencia (NES), una herramienta de código abierto para organizar, controlar y gestionar datos clínicos, neurofisiológicos y experimentales recopilados en hospitales e instituciones de investigación.

Este documento está dividido en 3 partes:

.. toctree::
   :maxdepth: 1
   :caption: Instalación
   :titlesonly:

   installation/installationtutorial
   installation/scriptinitialdata
   installation/admininterface
   installation/icddata3.0
   installation/dockercontainer

.. toctree::
   :maxdepth: 1
   :caption: LimeSurvey
   :titlesonly:

   limesurvey/limesurvey
   limesurvey/installlimesurvey
   limesurvey/guidelines
   limesurvey/integratenesandlimesurvey
   limesurvey/namingconventions
   limesurvey/bestpractices

.. toctree::
   :maxdepth: 1
   :caption: NeuroMat Open Database
   :titlesonly:

..   neuromatODb/neuromatodb
   neuromatODb/sendexperimentdata

.. toctree::
   :maxdepth: 1
   :caption: Guía de Usuario
   :titlesonly:

   userguide/userguide
   userguide/participants/participants
   userguide/studies
   userguide/publications
   userguide/questionnaires/questionnaires
   userguide/researchers
   userguide/setup/equipmentsetup
   userguide/export/export
   userguide/translation
   userguide/search
   userguide/permissions


.. toctree::
   :maxdepth: 1
   :caption: Videos
   :titlesonly:

..   videos/videos

.. toctree::
   :maxdepth: 1
   :caption: Training
   :titlesonly:

..   training/training

