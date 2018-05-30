.. _eeg-electrode-layout-settings:

EEG Electrode Layout Settings
=============================

The electrode layout setting involve the information related to the electrode configuration used in the acquisition of EEG raw data.

Electrode net setting
---------------------

This tab allows to register information about the electrode system used in the acquisition of EEG raw data. 
- :ref:`manufacturer`: the manufacturer of the electrode system used in the current experiment.
- :ref:`Equipment identification <eeg-electrode-net-cap>`: the name of the electrode net used in this experiment.
- :ref:`eeg-electrode-localization-system`: the system of the physical placement and designations of electrodes on the scalp. This system can be standardized (ex. International Federation in Electroencephalography and Clinical Neurophysiology) such as 10-20 system, 10-10 system, 10-5 system or can be a proprietary design of a specific manufacturer.

.. note:: If the wanted manufacturer, identification and/or the electrode localization system do not exist, they should be added in the :ref:`equipment-set-up` module.

.. image:: ../../../_img/eeg_electrode_layout_settings.png

Electrode position setting
--------------------------

In this tab is possible to see the image map of the electrode system selected. In the right side of the page is shown the electrode positions used in the experiment. The positions are labeled with the reference name of the system selected.  
In the editing mode is possible to change the electrode position used by clicking in the check box to enable or disable the position selected. The image map will change showing the choices done. 

.. note:: If the wanted image map to not exist, this should be added in the :ref:`equipment-set-up` module in the item Electrode Localization System. 

.. image:: ../../../_img/eeg_electrode_position.png

Electrode model setting
-----------------------

This tab shows a list with the electrode positions and the model of electrode used in each position. In the editing mode is possible change the model of a specific electrode.

.. note:: If the wanted electrode model does not exist, this should be added in the :ref:`equipment-set-up` module in the item :ref:`electrode-model`.

.. image:: ../../../_img/eeg_electrode_model_settings.png