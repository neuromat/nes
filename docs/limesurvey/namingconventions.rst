.. _naming-conventions-for-question-codes:

Convenciones de nomenclatura para códigos de preguntas
=====================================

Esta sección presenta una sugerencia sobre cómo nombrar códigos que identifican preguntas en LimeSurvey. 

Para facilitar la comprensión y manipulación de los datos recogidos mediante cuestionarios, recomendamos utilizar un prefijo en el código (identificador) de cada pregunta. La intención de este prefijo es informar el tipo de datos "recogidos" por la pregunta. Por ejemplo, para una pregunta como "¿Cuántos años tienes?", ``intAge`` sería un buen código. El prefijo ``int`` indica que el valor de la edad es un número entero.

La siguiente lista contiene sugerencias de prefijos para los tipos de respuestas más frecuentes:

* Todos los tipos de preguntas de opción única → ``lst``
* Todos los tipos de preguntas de opción múltiple → ``mul``
* Todos los tipos de preguntas de texto → ``txt``
* Matriz (números) → ``int`` o ``dec``
* Matriz (texto) → ``txt``
* Otros tipos de matriz → ``lst``
* Fecha/Hora → ``dat``
* Ecuación → ``equ``
* Entrada numérica → ``int`` o ``dec``
* Entrada numérica múltiple → ``int`` o ``dec``
* Sí/No → ``yn``
* Otros tipos de preguntas → ``txt``
