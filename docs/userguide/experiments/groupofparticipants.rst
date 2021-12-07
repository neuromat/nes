.. _group-of-participants:

Grupo de participantes
=====================

Los participantes de los experimentos se organizan en grupos.

.. _creating-and-editing-a-group:

Creación y edición de un grupo
----------------------------
Un grupo contiene:

* Un título (obligatorio);
* Una descripción (obligatoria);
* Uno o más diagnósticos de enfermedades especificadas utilizando la Clasificación Internacional de Enfermedades (CIE) como criterios de inclusión;
* Una lista de participantes; y
* Un protocolo experimental.

Sin embargo, al crear un nuevo grupo, la pantalla solo solicita el título y la descripción. Esos son también los campos que se pueden actualizar si hace clic en el botón 'Editar' en la pantalla de visualización. Se pueden agregar criterios de inclusión y protocolo experimental al visualizar un grupo. Solo los usuarios autorizados pueden actualizar un grupo, lo que significa el propietario del estudio del experimento de este grupo o los usuarios con permiso para cambiar los estudios de otros (Ver :ref:`permissions` para más información).

.. image:: ../../_img/edit_group.png

.. _visualizing-a-group:

Visualización de un grupo
-------------------
Mientras está en la pantalla para visualizar un experimento, puede ver más información sobre un grupo existente haciendo clic en su título en la lista de grupos. Mientras visualiza un grupo, puede eliminarlo haciendo clic en el botón `Delete` . Sin embargo, este botón sólo es visible para los usuarios que tienen permiso para actualizar el grupo.

.. image:: ../../_img/view_group.png

.. _inclusion-criteria:

Criterios de inclusión
------------------

Los investigadores pueden incluir uno o más diagnósticos que se utilizarán como criterios de inclusión para los participantes en el grupo. Esta información es sólo informativa. El sistema no verifica si los participantes incluidos en el grupo tienen la enfermedad especificada. Para incluir un nuevo diagnóstico, debe escribir el nombre o parte del nombre de la enfermedad o el código ICD. Se mostrará una lista desplegable de sugerencias para que seleccione uno de los diagnósticos de la lista. Para eliminar un criterio de inclusión, simplemente haga clic en el botón :x: asociado a él. Una vez más, solo los usuarios que tienen permiso para actualizar un grupo pueden agregar o quitar criterios de inclusión. Los usuarios no autorizados no pueden ver el campo de texto.

.. image:: ../../_img/icd.png

.. _questionnaires-of-the-experimental-protocol:

Cuestionarios del Protocolo Experimental
-------------------------------------------

Para ayudar a los usuarios a visualizar los datos ya recopilados de los participantes del grupo, la pantalla que muestra información detallada sobre un grupo tiene una sección específica que resume el número de rellenos para cada cuestionario del protocolo experimental. Cada línea muestra la identificación del cuestionario, el número de rellenos necesarios por participante, el número total de rellenos necesarios para el grupo y el número total de rellenos ya realizados. Al hacer clic en la identificación del cuestionario, puede ver una pantalla que muestra información detallada sobre el cuestionario y una lista de participantes. La lista incluye una representación gráfica del número de rellenos ya realizados por el participante en relación con el número de rellenos necesarios del participante y la fecha de cada llenado iniciado o terminado. La fecha es un enlace a una página que le permite terminar el relleno, en caso de un relleno incompleto, o una página que muestra las respuestas, en caso de un relleno completado. Ver :ref:`managing-a-questionnaire-fill` para más detalles.

.. image:: ../../_img/questionnaire_of_a_group_with_list_of_participants.png

.. listing-and-inserting-participants:

Listado e inserción de participantes
----------------------------------

Un grupo puede tener un número ilimitado de participantes. Si aún no se ha registrado ningún participante en el grupo, verá un boton `Add participant/s`. 

.. image:: ../../_img/group_new_participant.png

Si al menos un participante estaba registrado, verá un enlace cuyo texto informa el número de participantes ya registrados. Tanto este enlace como el boton `Add participant/s` llevará al usuario a una pantalla que permite registrar a un participante y enumera los participantes ya registrados. Si no tiene el [[permiso | Permisos]] para agregar un participante a un grupo, solo verá un mensaje que informa el número de participantes ya registrados.

Para registrar un nuevo participante, debe escribir el nombre o el ID del participante. Mientras el usuario escribe, el sistema sugiere participantes que coincidan con el término tipado. Las sugerencias se dan desde el primer carácter escrito. Cada sugerencia es un enlace. Al hacer clic en el vínculo, se incluye al participante en la lista de participantes registrados.

La lista de participantes inscritos incluye un enlace (:p aperclip:) a una pantalla que permite adjuntar/visualizar el fichero que almacena el plazo de consentimiento firmado por el participante, y una representación gráfica del número de cuestionarios ya cumplimentados (se han realizado todos los rellenos requeridos) por el participante en relación al número de cuestionarios incluidos en el protocolo experimental.

.. image:: ../../_img/list_of_participants.png

.. _visualizing-a-participant:

Visualización de un participante
-------------------------

Al hacer clic en el nombre del participante, se obtiene una pantalla que muestra todos los rellenos de este participante. Si tiene el :ref:`permissions` Para eliminar a un participante del grupo, también verá un boton `Delete` .

.. image:: ../../_img/participant_of_a_group.png

.. _experimental-protocol:

Protocolo Experimental
---------------------

Si aún no se ha configurado ningún protocolo experimental en el grupo, verá un boton `Configure / Create`. Si hace clic en este botón, NES mostrará la pantalla para crear o reutilizar un componente que se convertirá en la raíz del protocolo experimental del grupo. La raíz de un protocolo experimental siempre será un `set of steps`. Si no tiene el :ref:`permissions` Para cambiar el estudio, sólo verá un mensaje que informa de que no se ha configurado ningún protocolo experimental.

.. image:: ../../_img/no_experimental_protocol.png

Si la raíz del protocolo experimental ya ha sido configurada, verá un enlace cuyo texto informa la identificación del conjunto de pasos que es la raíz del protocolo experimental del grupo. Si hace clic en este enlace, NES mostrará la pantalla de visualización para este conjunto de pasos. Si tiene el :ref:`permission` Para cambiar el estudio, también verá un botón :x: que se puede utilizar para desconfigurar el protocolo experimental.

Encontrará más información sobre este tema en :ref:`configuring-an-experimental-protocol`.