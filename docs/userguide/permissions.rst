.. _permissions:

Permisos
===========

NES determina lo que se le permite hacer en él mirando los permisos que tiene.

.. _list-of-permissions-used-by-nes:

Lista de permisos utilizados por NES
-------------------------------

Un permiso es un indicador binario (sí/no) que designa si puede realizar una determinada tarea. Aquí está la lista de permisos que NES comprueba mientras usa el sistema:

* `Agregar ususario`
* `Cambiar usuario`
* `Borrar usuario`
* `Agregar participante`
* `Cambiar participante`
* `Ver participante`
* `Borrar participante`
* `Exportar participante`
* `Ver datos confidenciales de los participantes`
* `Agregar datos de registros médicos`
* `Ver datos de registros médicos`
* `Exportar datos de registros médicos`
* `Agregar cuestionarios`
* `Cambiar cuestionarios`
* `Ver listas de cuestionarios`
* `Eliminar cuestionarios`
* `Agregar respuesta al cuestionario`
* `Cambiar la respuesta al cuestionario`
* `Ver respuesta al cuestionario`
* `Eliminar la respuesta al cuestionario`
* `Exportar respuesta al cuestionario`
* `Añadir proyecto de investigación`
* `Proyecto de investigación del cambio`
* `Ver proyecto de investigación`
* `Eliminar proyecto de investigación`
* `Agregar experimento`
* `Experimento de cambio`
* `Eliminar experimento`
* `Proyecto de investigación de cambio creado por otros`
* `Registrar equipos`

.. _group-of-users-roles:

Grupo de Usuarios / Roles
----------------------
Para aplicar fácilmente permisos a más de un usuario, el administrador de NES puede crear grupos de usuarios. Mediante el uso de grupos, en lugar de aplicar permisos individuales directamente a los usuarios, el administrador aplica permisos a los grupos e incluye usuarios en uno o más grupos. De esta manera, si el grupo tiene un determinado permiso y un usuario está en este grupo, él o ella también tendrá este permiso.

En NES, tratamos a los grupos de usuarios como roles. Por lo tanto, aunque puede estar en más de un grupo (tener más de un rol), generalmente los permisos de un solo rol serán exactamente lo que necesita. Los roles que sugerimos para NES son `Administrador`, `Asistente`, `Fisioterapeuta`, `Doctor`, `Investigador Junior`, and `Investigador Senior`. Ver :ref:`script-for-creating-initial-data` para conocer los permisos que tiene cada rol. Sin embargo, utilizando el :ref: `administration-interface`, el administrador puede cambiar la lista de roles y los permisos para cada rol para que se adapte mejor a las necesidades del hospital o la institución de investigación.