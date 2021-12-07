.. _emg-digital-filter-settings:

Configuración del filtro digital EMG
===========================

En esta configuración puede registrar el tipo de filtro y la configuración utilizada en el experimento EMG. La siguiente imagen muestra la pantalla para registrar la configuración del filtro digital EMG:

.. image:: ../../../_img/emg_digital_filter_settings.png

Los canales de grabación del dispositivo EMG están equipados con filtros ajustables de paso alto y paso bajo mediante los cuales la respuesta de frecuencia se puede restringir a la banda de frecuencia de interés.
Esta configuración permite registrar la información sobre el filtro utilizado en cada experimento. La información que se puede registrar son las siguientes:

* :ref:`filter-type`: Una vez que se almacenan los datos, se puede utilizar el filtrado digital. Es posible elegir entre el filtrado lineal (FIR, IIR) o nuevos métodos de filtrado no lineal. La elección debe hacerse de acuerdo con los objetivos puestos en el procesamiento de la señal.
* Corte de paso alto (Hz): es un filtro que pasa señales con una frecuencia superior a una cierta frecuencia de corte y atenúa las señales con frecuencias inferiores a la frecuencia de corte.
* Corte de paso bajo (Hz): es un filtro que pasa señales con una frecuencia inferior a una cierta frecuencia de corte y atenúa las señales con frecuencias superiores a la frecuencia de corte.
* Rango de paso de banda (Hz): un filtro de paso de banda es un dispositivo que pasa frecuencias dentro de un cierto rango y rechaza (atenúa) frecuencias fuera de ese rango.
* Rango de muesca (Hz): también llamado filtro de parada de banda o filtro de rechazo de banda es un filtro que pasa la mayoría de las frecuencias inalteradas, pero atenúa las de un rango específico a niveles muy bajos. Es lo opuesto a un filtro de paso de banda. Un filtro de muesca es un filtro de parada de banda con una banda de parada estrecha.
* Orden: es el retardo máximo, en muestras, utilizado en la creación de cada muestra de salida. De manera específica, el orden del filtro es la duración (efectiva) de la respuesta al impulso. Su unidad de medida es entera

.. nota:: Si el tipo de filtro no existe, debe agregarse en el cuadro :ref:`equipment-set-up` .