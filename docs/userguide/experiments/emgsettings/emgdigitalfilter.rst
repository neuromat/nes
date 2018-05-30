.. _emg-digital-filter-settings:

EMG Digital Filter Settings
===========================

In this settings you can register the type of filter and the configuration used in the EMG experiment. The picture below show the screen for register the EMG digital filter settings:

.. image:: ../../../_img/emg_digital_filter_settings.png

The EMG device recording channels are equipped with adjustable high pass and low pass filters by which the frequency response can be restricted to the frequency band of interest.
This setting allows to register the information about the filter used in each experiment. The information that can be registered are the following:

* :ref:`filter-type`: Once data are stored, digital filtering can be used. It is possible to choose from linear (FIR, IIR) filtering or novel non-linear filtering methods. The choice should be done according to the objectives put on the signal processing.
* High pass cutoff (Hz): is a filter that passes signals with a frequency higher than a certain cutoff frequency and attenuates signals with frequencies lower than the cutoff frequency.
* Low pass cutoff (Hz): is a filter that passes signals with a frequency lower than a certain cutoff frequency and attenuates signals with frequencies higher than the cutoff frequency.
* Band pass range (Hz): a band-pass filter is a device that passes frequencies within a certain range and rejects (attenuates) frequencies outside that range.
* Notch range (Hz): also called a band-stop filter or band-rejection filter is a filter that passes most frequencies unaltered, but attenuates those in a specific range to very low levels. It is the opposite of a band-pass filter. A notch filter is a band-stop filter with a narrow stopband.
* Order: is the maximum delay, in samples, used in creating each output sample. In specific way the filter order is the (effective) impulse response duration. Its unit of measurement is integer

.. note:: If the filter type does not exist, this must to be added in the :ref:`equipment-set-up` module.