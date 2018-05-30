.. _configuring-an-experimental-protocol:

Configuring an Experimental Protocol
====================================

Each group of participant may have an experimental protocol, which is composed of steps. Details about the different types of steps are given in :ref:`managing-steps-for-experimental-protocol`.

.. _creating-and-editing-a-set-of-steps:

Creating and Editing a Set of Steps
-----------------------------------

A `set of steps` contains:

* An identification (obligatory);
* A description;
* A duration;
* A type of organization of its sub-steps (obligatory);
* A number of obligatory sub-steps (obligatory); and
* A list of sub-steps.

However, while creating a new set of steps or updating an existing one, the screen does not ask for the sub-steps. You can add sub-steps while visualizing a set of steps. The possible types of organization of the sub-steps are: `In a sequence`, which means that the steps will be executed one after the other in the order you defined, or `In parallel`, which means that all steps will be executed at the same time. You can't edit the duration of a set of steps, because this value is calculated automatically. If the set of steps is sequential, the duration is defined as the sum of the duration of each sub-step of the set, else, namely a parallel set of steps, it is defined as the duration of the longest sub-step of the set. The number of obligatory sub-step indicates if all sub-steps should be executed while executing the set of steps (this is the default behavior), or if only a subset, whose size should be indicated in the text field, should be executed.

.. image:: ../../_img/edit_set_of_steps.png

.. _visualizing-a-set-of-steps:

Visualizing a Set of Steps
--------------------------

The screen for visualizing a sequential set of steps will show two sections related to its sub-steps. The first one, called `Steps with fixed position`, lists the use of steps that are a sub-step of the set in the order they should be executed. If the set uses a step in a random position inside the sequence, this step is not listed in this section. Instead, this section will contain a line for each step with a random position, so that you can indicate the exact position of the fixed steps in relation to the positions reserved to random steps. The random step itself is listed in the second section, called `Steps with random position`. You can define if the use of a step has a fixed or random position while `inserting a use of a step` in the set of steps, or while `editing a use of a step. If the set of steps contains only random positioned sub-step, the section for fixed positioned uses will not show a placeholder for each random positioned child, instead, it will only inform that there is no fixed positioned use of step.

.. image:: ../../_img/view_set_of_steps.png

The screen for visualizing a parallel set of steps will show only one section related to its sub-steps, without a title. In this case, the use of steps is listed alphabetically, considering first the type, then the identification, and then the name of use.

To reduce the use of screen space, when more than one use of the same step (not the same type of step) appears together, the interface automatically create an `accordion <https://en.wikipedia.org/wiki/Accordion_(GUI)>`_ to group them and indicating how many uses of the step are aggregated in it. Clicking the accordion expands it, showing all the uses inside it. Several placeholders for random positioned uses of steps are also aggregated in an accordion.

.. image:: ../../_img/view_set_of_steps_with_expanded_accordions.png

Each use of step with fixed position contains :arrow_up: and :arrow_down: buttons so that you can change the order in which the step should be executed. Accordions that group fixed positioned sub-steps also shows the arrow buttons. If you use the arrows of the accordions you'll move all the uses of steps that it aggregates with it. Note that if you move a single step or an accordion in the direction of a second accordion, only one element of the second accordion will be jumped. Thus, the jumped step will no longer be part of the second accordion. Only authorized users will see the arrow buttons.

Each sub-step of a set of steps will show a :x: button, that allows you to remove this use of step from the set. This operation does not delete the step from NES. You'll still be able to find it in the list of steps of the experiment. Only authorized users will see the :x: buttons. Remember: to delete a step from the system, including sets of steps, you have to click the *Delete* button, while visualizing the step you want to remove. However, this button is visible only for the users that have permission to update the experiment.

.. inserting-a-use-of-a-step:

Inserting a Use of a Step
-------------------------

To insert a step in the set of steps, you should click a `Insert step` button and choose the type of step you want to include from the drop down list. A sequential set of steps has two `Insert step` buttons, one in the section for fixed positioned sub-step an the other in the section for random positioned sub-step. Then, you will see a screen that allows the creation of a new step or the reuse of an already created one. The default options is the creation of a new step. In this case you have to fill the fields for the type of step you are creating.

.. image:: ../../_img/insert_new_step.png

If you want to reuse an existing step, click the drop down list shown just bellow the title of the first section of the screen. A list with the existing steps of the type you want will be shown. After selecting one, the screen will show the information about it, without giving you the option to edit it.

.. image:: ../../_img/reuse_step.png

The second section of the screen allows you to specify the number of uses of the step that you want to include. This is just a shortcut that avoids the need to include one use at a time. All the uses will be included at the end of the sub-step list. You can then reorder them as you wish.

.. _editing-a-use-of-a-step:

Editing a Use of a Step
-----------------------

The identification of a step shown in the list of sub-steps is a link to a screen that allows updating information about the use of the step. A use of step may have a name, that is useful to differentiate two or more uses of the same step. If the step is used in a sequential set of steps, you will be able to change the type of position it has in the sequence from `Fixed` to `Random` or vice versa. You can also set the number of times you want this step to be repeated. Default value for this field is one.

.. image:: ../../_img/edit_use_of_step.png

If you change the number of repetitions to `Unlimited`, or if you set a value greater than one, a new field will be shown, allowing you to set the interval between repetitions. The interval may be `Undefined` or may be set by a value and a unit.

.. image:: ../../_img/edit_use_of_step_with_interval.png

Observe that setting the number of repetitions is not the same as inserting multiple uses of the same step, as explained in the previous section. It is preferable to include only one use and to specify the number of repetitions, because it will let your set of steps cleaner and because it allows you to specify an interval between repetitions without the need to explicitly include pause steps. You should use multiple uses of the same step if you want them to be intercalated with other steps.