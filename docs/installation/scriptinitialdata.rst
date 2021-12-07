.. _script-for-creating-initial-data:

Script para crear datos iniciales
================================

Después de instalar NES, todo lo que tiene en la base de datos es un solo usuario. Sin embargo, hay algunos datos que todas las bases de datos de NES deberían tener, como ciertos grupos de usuarios, opciones relacionadas con los campos que describen a los participantes y tipos de estímulos. Para facilitar el proceso de escritura de estos datos en la base de datos, el equipo de desarrollo ha creado un script. La versión actual de NES ofrece solo un script que crea estos datos en portugués. Una versión en inglés del script estará disponible en la próxima versión de NES. 

.. _initial-data-created-by-the-script:

Datos iniciales creados por el script
----------------------------------
Los primeros datos creados por el script son los grupos de usuarios, cada uno con un contenido específico :ref:`permissions`. Seis grupos son creados:

Administrador
`````````````
* *Agregar usuario*
* *Cambiar usuario*
* *Borrar usuario*

Asistente
`````````
* *Agregar participante*
* *Cambiar participante*
* *Ver participante*
* *Borrar participante*

Fisioterapeuta
```````````````
* Los mismos permisos de un asistente
* *Ver datos de registros clínicos*
* *Ver listas de cuestionarios*
* *Agregar cuestionarios*
* *Cambiar cuestionarios*
* *Eliminar cuestionarios*
* *Agregar respuesta al cuestionario de entrada*
* *Cambiar respuesta al cuestionario de ingreso*
* *Ver respuesta al cuestionario de entrada*
* *Eliminar la respuesta al cuestionario de entrada*

Doctor
``````
* Mismos permisos de un fisioterapeuta
* *Agregar datos de registros clínicos*

Investigador Junior
`````````````````
* Mismos permisos de un fisioterapeuta
* *Añadir proyecto de investigación*
* *Proyecto de investigación del cambio*
* *Ver proyecto de investigación*
* *Eliminar proyecto de investigación*
* *Agregar experimento*
* *Experimento de cambio*
* *Eliminar experimento*
* *Agregar respuesta al cuestionario del experimento*
* *Respuesta al cuestionario del experimento de cambio*
* *Ver respuesta al cuestionario del experimento*
* *Eliminar la respuesta al cuestionario del experimento*
* *Agregar participante a un grupo*
* *Cambiar de tema de un grupo*
* *Eliminar participante de un grupo*
* *Registrar equipos*

Investigador Senior
`````````````````
* Los mismos permisos de un investigador junior
* *Cambio de proyecto de investigación perteneciente a otros*
* *Participante de exportación*
* * Exportar registro médico *
* *Respuesta al cuestionario de entrada a la exportación*
* * Ver datos confidenciales de los participantes *

A continuación, el script crea opciones relacionadas con los campos que describen a un participante. Esto se hace para 9 conjuntos de opciones:

**Frecuencia de consumo de alcohol**

* Todos los días
* Todos los fines de semana
* Esporádicamente

**Periodo de consumo de alcohol**

* Más de 10 años
* 5-10 años
* 1-5 años
* Menos de 1 año

**Cantidad de cigarrillos**

* Más de 3 packs
* 1-2 paquetes
* Menos de 1 paquete

**Color de piel**

* Amarillo
* Blanco
* Indígenas
* Marrón
* Negro

**Género**

* Masculino
* Femenino

**Estado civil**

* No informado
* Viudo
* Separados/Divorciados
* Casados/Vivir juntos
* Sencillo

**Pago**

* Privado
* Seguro de salud
* Sistema público de salud brasileño

**Religión**

* Budismo
* Candomblé
* Católica
* Espírita
* Evangélico
* La Iglesia de Jesucristo de los Santos de los Últimos Días
* Judaísmo
* Protestante
* Religiones orientales
* Sin religión
* Testigos de Jehová
* Umbanda

**Educación**

* Graduado
* Terminó la escuela secundaria
* Terminó la escuela secundaria
* Terminó la escuela primaria
* Analfabeto / No terminó la escuela primaria

Finalmente, el script crea **tipos de estímulos**

* Auditiva
* Gustativo
* Interoceptivo
* Olfativo
* Somatosensorial
* Visual

.. _running-the-script:

Ejecución del script
------------------
Para ejecutar el script, debe ejecutar los siguientes comandos.

#. Introduzca la carpeta donde se encuentra el script::

    cd [folder where NES is installed]/patientregistrationsystem/qdc

#. Conceder permiso de ejecución al script::

    chmod +x add_initial_data.py

#. Ejecutar el script::

    python manage.py shell < add_initial_data.py