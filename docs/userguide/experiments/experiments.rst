.. _experiments:

Experimentos
===========

Cada estudio puede tener varios experimentos. Para gestionar un experimento, NES proporciona una página donde se pueden registrar todos los detalles y la configuración del mismo. Esta sección trata sobre experimentos y se divide en los siguientes temas::

* `Creación y edición de un experimento`_
* `Visualización de un experimento`_
* `Exportación de un experimento`_
* :ref:`investigadores de un experimento`
* :ref:`grupo de participantes`
* :ref:`datos sin procesar y archivos adicionales`
* :ref:`configuración de grabación`
* :ref:`managing-steps-for-experimental-protocol`
* :ref:`configurar-un-protocolo-experimental`
* :ref:`Cómo enviar datos de experimentos desde NES`

.. _creating-and-editing-an-experiment:

Creación y edición de un experimento
----------------------------------

Para crear un experimento, NES permite registrar información relevante sobre el mismo. Un experimento contiene:

* **Un título:** título del experimento (obligatorio);
* **Una descripción:** breve descripción sobre el experimento (obligatorio);
* **URL de información del proyecto:** URL del proyecto al que pertenece el experimento, si existe;
* **URL del proyecto aprobado por el comité de ética:** Url que remite al comité de ética.
* **Expediente del proyecto aprobado por el comité de ética:** Carga del archivo de la aprobación por parte del comité de ética.

.. image:: ../../_img/experiment_create.png

Después de registrar la información principal del experimento, puede comenzar a configurar el experimento registrando información como:

* Una lista de :ref:`group-of-participants`: grupo de participantes involucrados en el experimento. Un experimento puede tener un número ilimitado de grupos de participantes. Solo los usuarios autorizados pueden ver el boton `Insert new` e incluir nuevos grupos en un experimento.
* :ref:`Equipment settings <recording-settings>`: registro de la configuración de los equipos involucrados en la adquisición de datos. 
* Una lista de :ref:`steps for experimental protocol <managing-steps-for-experimental-protocol>`: descripción del protocolo experimental utilizado por cada grupo de participantes. Un protocolo experimental se compone de pasos, que pueden ser de uno de los siguientes tipos: `instruction`, `pause`, `questionnaire`, `stimulus`, `task for participant`, `task for the experimenter`, `EEG`, `EMG`, `TMS`, `goalkeeper game phase`, `generic data collection` o otros `set of steps`. Se puede usar un solo paso más de una vez en el mismo experimento. El protocolo de un experimento se define organizando los usos de los pasos de una manera que determina el momento en el que deben suceder. Esto se hace dentro de cada grupo de participantes, porque el protocolo experimental de un grupo puede ser diferente del protocolo experimental de otro grupo. Sin embargo, como es posible utilizar un paso específico en más de un grupo, se accede a la pantalla para :ref:`managing-steps-for-experimental-protocol` desde la pantalla para visualizar el experimento.

.. _visualizing-an-experiment:

Visualización de un experimento
-------------------------

Mientras está en la pantalla para visualizar un estudio, puede ver más información sobre un experimento existente haciendo clic en su título en la lista de experimentos. Se muestra una página con el detalle del experimento (ver figura a continuación). A través de esta página es posible gestionar los ajustes del experimento, los grupos, las configuraciones de los equipos y el protocolo experimental.
Además, puede eliminar el experimento haciendo clic en el botón *Eliminar*. Sin embargo, este botón sólo es visible para los usuarios que tienen :ref:`permissions` Para actualizar el experimento.

.. image: ../../_img/experiment_view.png

.. _exporting-an-experiment:

Exportación de un experimento
-----------------------

Puede exportar un experimento haciendo clic en el botón `Export experiment` icono en el lis de los experimentos de un estudio (véase :ref:`_exporting-importing-an-experiment-of-a-study`) o haciendo clic en el botón Exportar en la parte inferior de la página de descripción del experimento, si tiene los permisos correctos.

.. image: ../../_img/experiment_export.png

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :hidden:

   researchersofanexperiment
   groupofparticipants
   rawdataandadditionalfiles
   recordsettings
   managingstepsforep
   configuringep