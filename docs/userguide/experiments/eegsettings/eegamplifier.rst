.. _eeg-amplifier-settings:

EEG Amplifier Settings
======================

The signals need to be amplified to make them compatible with devices such as displays, recorders, or A/D converters. Amplifiers adequate to measure these signals have to satisfy very specific requirements. They have to provide amplification selective to the physiological signal, reject superimposed noise and interference signals, and guarantee protection from damages through voltage and current surges for both patients and electronic equipment. The EEG amplifier settings page allows to register settings about the EEG amplifier used in the experiment. The information registered here are:

* :ref:`manufacturer`: The name of the amplifier manufacturer;
* :ref:`amplifier`: The model name of the amplifier. When the Identification is selected some informations about the amplifier are shown, such as the description and gain;
* **Configured gain:** In this item is registered the gain used in the experiment. An amplifier multiplies an input voltage by a constant usually lying in the range of up to 1000000. The amplification factor is referred to as gain and may be expressed as Vout/ Vin. The unit of the gain is the decibel (dB): dB = 20 X log(Vout/Vin);
* **Sampling Rate:** Number of discrete samples that are taken of the continuous voltages per some unit of time. The unit used here is hertz (Hz), representing the number of samples per second; and
* **Number of used channels**.

.. note:: If the manufacturer and/or Identification does not exist, it has to be added in the :ref:`equipment-set-up` module.

.. image:: ../../../_img/eeg_amplifier_settings.png