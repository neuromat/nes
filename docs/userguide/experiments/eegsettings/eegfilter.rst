.. _eeg-filter-settings:

EEG Filter Settings
===================

The fact that the potential differences fluctuate as a function of time implies that the recorded EEG signals have a certain bandwith. For the majority of EEG investigations the recorded signal lies between 1 Hz and 70 Hz. Information will be lost if the frequency response of the recording channel is narrower than the frequency range of the EEG signal. If the frequency range of the recording channel is wider than the bandwith of the EEG signal, noise in the recorded data will contain additional irrelevant information. EEG recording channels are equipped with adjustable high pass and low pass filters by which the frequency response can be restricted to the frequency band of interest.
This setting allows to register the information about the filter used in each experiment. The information that can be registered are the following:

* :ref:`filter-type`: Once data are stored, digital filtering can be used. It is possible to choose from linear (FIR, IIR) filtering or novel non-linear filtering methods. The choice should be done according to the objectives put on the signal processing;
* High pass cutoff(Hz): is a filter that passes signals with a frequency higher than a certain cutoff frequency and attenuates signals with frequencies lower than the cutoff frequency;
* Low pass cutoff(Hz): is a filter that passes signals with a frequency lower than a certain cutoff frequency and attenuates signals with frequencies higher than the cutoff frequency;
* Low band pass (Hz): a band-pass filter is a device that passes frequencies within a certain range and rejects (attenuates) frequencies outside that range. This field represents the lowest value of this range;
* High band pass (Hz): a band-pass filter is a device that passes frequencies within a certain range and rejects (attenuates) frequencies outside that range. This field represents the highest value of this range;
* Low Notch (Hz): also called a band-stop filter or band-rejection filter is a filter that passes most frequencies unaltered, but attenuates those in a specific range to very low levels. It is the opposite of a band-pass filter. A notch filter is a band-stop filter with a narrow stopband. This is the lowest value of this range;
* High Notch (Hz): complementary to Low Notch, this is the highest value of this range.
* Order: is the maximum delay, in samples, used in creating each output sample. In specific way the filter order is the (effective) impulse response duration. Its unit of measurement is integer

.. note:: If the filter type does not exist, this has to be added in the :ref:`equipment-set-up` module.

.. image:: ../../../_img/eeg_filter_settings.png