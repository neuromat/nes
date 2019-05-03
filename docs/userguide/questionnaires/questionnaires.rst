.. _questionnaires:

Questionnaires
==============

Questionnaires are a very flexible way to collect data from a participant. In NES, a questionnaire may or may not have required filling. Experiment questionnaires are configured as a step in the experimental protocol of a :ref:`group <group-of-participants>`. Questionnaires that haven't required filling are useful to collect data that are not foreseen in the :ref:`participant's section <participants>`. Any questionnaire can have both functions.

.. _questionnaires-list:

Questionnaires List
-------------------

In order to access all questionnaires registered at NES, click `Questionnaires` menu item and the `Questionnaire List` will show up displaying the informations about each questionnaire, namely `limesurvey ID`, `title`, if its `fill is required` and if the `questionnaire is or isn’t active` at LimeSurvey. Now, as this is an expensive call to LimeSurvey API, the informations are saved in the database at the moment of its registration at NES. If you want to update the informations of that list, you will need to click in the `Update` button at the bottom of the page. This might take a while depending of how many questionnaires you have registered.

.. image:: ../../_img/questionnaire_list.png

This screen allows you to:

* :ref:`Insert a New Questionnaire <inserting-a-new-questionnaire>`
* :ref:`View a Questionnaire <viewing-a-questionnaire>`

.. _inserting-a-new-questionnaire:

Inserting a New Questionnaire
-----------------------------

Click the `Insert new questionnaire` button to include a new questionnaire.

.. image:: ../../_img/questionnaire_insert.png

From the questionnaire list, you select the questionnaire you want to register. Questionnaires in this list were previously created in LimeSurvey (see :ref:`limesurvey` to learn how to create a new questionnaire).

If this questionnaire has required filling, you have to click the `Required fill` checkbox.

Click either `Save` button to include the questionnaire, or `Cancel` to go back to previous page without saving.

.. _viewing-a-questionnaire:

Viewing a Questionnaire
-----------------------

To see more information about a specific questionnaire, click on the questionnaire link.

.. image:: ../../_img/questionnaire_view_experiment.png

You are seeing 4 sections:

* `Questionnaire Information`_
* `Sensitive Questions`_
* `Answered by Participants`_
* `Used in Experiments`_

.. _questionnaire-information:

Questionnaire Information
`````````````````````````

.. image:: ../../_img/questionnaire_view_information.png

If you click the `Edit` button, you can change the questionnaire type. Mark the checkbox to indicate that this questionnaire should be answered by all participants registered at NES. Unmark the checkbox if this questionnaire can only be answered from inside an experiment. Questionnaires that have required filling can also be used inside an experiment.

.. image:: ../../_img/questionnaire_edit_information.png

.. _sensitive-questions:

Sensitive Questions
```````````````````

.. image:: ../../_img/questionnaire_view_sensitive_questions.png

If you click the `Edit` button, you can choose which questions are about sensitive information. Mark the checkbox to indicate that question should be marked as sensitive. Unmark the checkbox otherwise. Click either `Save` button to mark the sensitive questions, or `Cancel` to go back to previous page without saving.

.. image:: ../../_img/questionnaire_edit_sensitive_questions.png

.. _answered-by-participants:

Answered by Participants
````````````````````````

This section shows all the participants that have filled the questionnaire. Even if the questionnaire don't have the filling required anymore, the fills made while it was required are also listed here. If it has required filling, you will also see all the participants who should answer this questionnaire.

.. image:: ../../_img/questionnaire_view_entrance_evaluation.png

You can't start or continue a fill here. If you want to fill it, look at the :ref:`answering-a-questionnaire` section on Participant Questionnaires page.

.. _used-in-experiments:

Used in Experiments
```````````````````

This section shows in which experimental protocols this questionnaire is used and the name of the participant who answered on it.

.. image:: ../../_img/questionnaire_view_use_in_experiments.png

This is only an informative section. To be able to start or continue a fill or to get more information about the fields see :ref:`questionnaires-of-the-experimental-protocol`.

.. _deleting-a-questionnaire:

Deleting a Questionnaire
````````````````````````

If you have the right :ref:`permissions`, you can stop using this questionnaire in NES by clicking the `Delete` button.

.. image:: ../../_img/questionnaire_delete.png

A confirmation pop-up will be shown. Click either the `Delete` button to confirm deletion or Cancel` button if you don't want to delete the questionnaire.

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :hidden:

   managingaquestionnairefill
   answeringalimesurveyquestionnaire