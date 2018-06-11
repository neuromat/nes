.. _managing-steps-for-experimental-protocol:

Managing Steps for Experimental Protocol
========================================

An experimental protocol is composed of steps. A single step may be used more than once in the same experiment. The protocol of an experiment is defined by organizing the uses of steps in a way that determines the moment in which they should happen. This is done inside each group of participant, because the experimental protocol of a group might be different from the experimental protocol of another group. NES allows register the following types of steps:

.. _list-of-steps:

List of Steps
-------------

All the steps already created for specifying the protocols of the experiments are listed when you click the `Manage` button while visualizing an :ref:`experiments`. Steps that are still not in use anywhere in the experiment are also listed.

.. image:: ../../_img/list_of_steps.png

From this screen, you can create new steps by clicking the `Insert New Step` button and choosing one of the available types. All types have at least an identification, and may have a description and a duration, which is composed of a value and a unit. Possible units are: millisecond, second, minute, hour, day, week, month and year. From this screen you can also see / edit information of a specific step by clicking the link that shows its identification. While viewing / editing a step, you can delete it by clicking the *Delete* button. However, this button is visible only for the users that have :ref:`permissions` to update the experiment. If you remove a step, you are also removing all the uses of this step.

See the following sections for specificities of each type of step:

.. _instruction-step:

Instruction
-----------

An `instruction` contains:

* An identification (obligatory);
* A description;
* A duration;
* The text of the instruction (obligatory); and
* Additional files.

.. image:: ../../_img/edit_instruction.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _pause-step:

Pause
-----

A `pause` contains:

* An identification (obligatory);
* A description; and
* A duration (obligatory); and
* Additional files.

.. image:: ../../_img/create_pause.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _questionnaire-step:

Questionnaire
-------------

A `questionnaire` contains:

* An identification (obligatory);
* A description;
* A duration;
* The name of a questionnaire at LimeSurvey (obligatory); and
* Additional files.

.. image:: ../../_img/edit_questionnaire.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _set-of-steps:

Set of Steps
------------

The `set of steps` is a special type of step, because it is used to aggregate uses of other steps in a way that defines the moment in which they should happen. Thus, we explain about a `set of steps` in detail in :ref:`configuring-an-experimental-protocol`.

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _stimulus-step:

Stimulus
--------

A `stimulus` contains:

* An identification (obligatory);
* A description;
* A duration;
* A type (obligatory);
* A media file containing the file of the stimulus; and
* Additional files.

The type of stimulus may be one of the types registered in the NES database. The :ref:`script-for-creating-initial-data` includes the following types: Auditory, Olfactory, Visual, Somatosensory, Interoceptive and Gustative.

.. image:: ../../_img/stimulus_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _task-step:

Task for the Experimenter or Task for the Subject
-------------------------------------------------

Both a `task for the experimenter` or a `task for the subject` contains:

* An identification (obligatory);
* A description;
* A duration; and
* Additional files.

.. image:: ../../_img/edit_task_for_the_participant.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _eeg-step:

EEG
---

A `EEG` step represents that an `Electroencephalography <https://en.wikipedia.org/wiki/Electroencephalography>`_ will be performed at this moment of the experiment. The setting of this step must be registered previously and defines how all EEG equipment are configured. An EEG step contains:

* An identification (obligatory);
* A duration;
* A description; and
* An EEG setting (obligatory).

.. image:: ../../_img/eeg_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _emg-step:

EMG
---

An `EMG` step represents that an `Electromyography <https://en.wikipedia.org/wiki/Electromyography>`_ will be performed at this moment of the experiment. An EMG step contains:

* An identification (obligatory);
* A duration;
* A description; and
* An EMG setting (obligatory).

.. image:: ../../_img/emg_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _tms-step:

TMS
---

An `TMS` step represents that a `Transcranial Magnetic Stimulation <https://en.wikipedia.org/wiki/Transcranial_magnetic_stimulation>`_ will be performed at this moment of the experiment. An TMS step contains:

* An identification (obligatory);
* A duration;
* A description; and
* An TMS setting (obligatory).

.. image:: ../../_img/tms_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _goalkeeper-game-phase:

Goalkeeper game phase
---------------------

An `Goalkeeper game phase` step represents that an `Goalkeeper game phase <http://game.numec.prp.usp.br>`_ will be performed at this moment of the experiment. An Goalkeeper game phase step contains:

* An identification (obligatory);
* A duration;
* A description;
* The software version of the Goalkeeper game used in the experiment (obligatory); and
* The context tree (obligatory).

.. image:: ../../_img/goalkeeper_game_phase_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`

.. _generic-data-collection:

Generic data collection
-----------------------

A `Generic data collection` contains:

* An identification (obligatory);
* A description;
* A duration; and
* A type (obligatory).

The type of Generic data collection may be one of the types registered in the NES database. They can be of the following types: kinematic measures, Stabilometry, Response time, Psychophysical measures, Verbal response, Psychometric scale, Unit recording and Multiunit recording.

.. image:: ../../_img/generic_data_step.png

:ref:`Back to top <managing-steps-for-experimental-protocol>`