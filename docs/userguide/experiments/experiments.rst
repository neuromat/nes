.. _experiments:

Experiments
===========

Each study can have several experiments. To manage an experiment, NES provide a page where all details and configuration of it can be registered. This section is about experiments and it is divided into the following topics:

* `Creating and Editing an Experiment`_
* `Visualizing an Experiment`_
* `Exporting an Experiment`_
* :ref:`researchers-of-an-experiment`
* :ref:`group-of-participants`
* :ref:`raw-data-and-additional-files`
* :ref:`recording-settings`
* :ref:`managing-steps-for-experimental-protocol`
* :ref:`configuring-an-experimental-protocol`
* :ref:`how-to-send-experiment-data-from-nes`

.. _creating-and-editing-an-experiment:

Creating and Editing an Experiment
----------------------------------

To create an experiment, NES allows to register relevant information about it. An experiment contains:

* **A title:** title of the experiment (obligatory);
* **A description:** brief description about the experiment (obligatory);
* **Project info URL:** Url of the project to which the experiment belongs, if it exists;
* **URL of the project approved by the ethics committee:** Url that refers the ethics committee.
* **Project file approved by the ethics committee:** Upload of the file of the approval by the ethics committé.

If the :ref:`NeuroMat Open Database <neuromat-open-database>` is :ref:`configured <how-to-send-experiment-data-from-nes>`, the following fields will be displayed:

* **Is public:** Checkbox to indicate if the experiment will be published.
* **Data acquisition is concluded:** Checkbox to indicate if the data acquisition of all participants in the experiment is completed.

.. image:: ../../_img/experiment_create.png

After register the experiment primary information you can start configuring your experiment registering informations such as:

* A list of :ref:`group-of-participants`: group of participants involved in the experiment. An experiment can have an unlimited number of group of participants. Only authorized users can see the `Insert new` button and include new groups to an experiment.
* :ref:`Equipment settings <recording-settings>`: record of the settings of the equipments involved at the data acquisition. 
* A list of :ref:`steps for experimental protocol <managing-steps-for-experimental-protocol>`: description of the experimental protocol used by each group of participants. An experimental protocol is composed of steps, that may be of one of the following types: `instruction`, `pause`, `questionnaire`, `stimulus`, `task for participant`, `task for the experimenter`, `EEG`, `EMG`, `TMS`, `goalkeeper game phase`, `generic data collection` or another `set of steps`. A single step may be used more than once in the same experiment. The protocol of an experiment is defined by organizing the uses of steps in a way that determines the moment in which they should happen. This is done inside each group of participant, because the experimental protocol of a group might be different from the experimental protocol of another group. However, as it is possible to use a specific step in more than one group, you access the screen for :ref:`managing-steps-for-experimental-protocol` from the screen for visualizing the experiment.

.. _visualizing-an-experiment:

Visualizing an Experiment
-------------------------

While in the screen for visualizing a study, you can see more information about an existing experiment by clicking on its title in the list of experiments. A page with the detail of the experiment is displayed (see figure below). Through this page is possible manage the experiment settings, groups, equipment configurations and the experimental protocol.
Also, you can delete the experiment by clicking the *Delete* button. However, this button is visible only for the users that have :ref:`permissions` to update the experiment.

.. image: ../../_img/experiment_view.png

If the experiment was sent to the NeuroMat Open Database, then it will be showing the experiment sending status. The information about the "Last update of the experiment" and "Last sending status" will be shown as well. To know how to make an experiment publicly available go to :ref:`how-to-send-experiment-data-from-nes`.

.. image: ../../_img/experiment_data_sending_status.png

.. _exporting-an-experiment:

Exporting an Experiment
-----------------------

You can export an experiment by clicking in the `Export experiment` icon in the lis of experiments of a study (see :ref:`_exporting-importing-an-experiment-of-a-study`) or by clicking the Export button at the bottom of the page of description of the experiment, if you have the right permissions.

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
