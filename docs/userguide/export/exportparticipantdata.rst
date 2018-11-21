.. _export-participant-data:

Export Participant Data
=======================

In the exportation by participant, you can filter of which participants you want get the data. You can choose between all participants or filter them by gender, marital status, locations, diagnosis and/or age. A list of the participants that go through the filter is shown. Clicking in the `Next` button, you go to the `Structure and fields selection` as you can see in the image bellow:

.. image:: ../../_img/export_participant_data.png

.. _general-information-export-participant:

General Information
-------------------

In this section, you are able to configure the structure of the directory where the questionnaires will be stored, the questionnaires evaluation headings and responses format that will be exported from information at LimeSurvey.
This options only make sense if you set up at least one questionnaire for exporting.

.. image:: ../../_img/general_information_export.png

Directory structure for evaluation questionnaire. You can choose either one or both options checked. You should not leave all the options unchecked.  All of them are checked by default.

A questionnaire evaluation data contains 2 types of information: headings, that are presented in the first line of export, and responses, that contains the lines with the selected fields from questionnaire evaluation. 

There are 3 types of headings:

* Question code; 
* Full question text;
* Abbreviated question text (partial question text is presented);

Only one choice can be checked.

Responses types for export are:

* Answer codes;
* Full answers;

Either one or both options can be checked. You should not leave all the options unchecked.  

.. _questionnaire-information-export-participant:

Format files can be choose in two types:

* CSV (Comma Separated Values);
* TSV (TabSeparated Values);

Only one choice can be checked.

Questionnaire Information
-------------------------

A list of questionnaires evaluation that contain the information selected from filters (first pages, as shown :ref:`here <export>` that select them is presented. 
A circle in blue (blue counter) presents the quantity of fields selected in each questionnaire. At the beginning, as there are no elements selected, zero is presented in all of them.

.. image:: ../../_img/questionnaire_information_export.png

In order to select the fields for specific questionnaire, click in the questionnaire link and a double list with fields drop down: `Fields available` and `Fields chosen` lists. There are many ways to select the fields:

* double click a specific field from `Fields available` list;
* click in one field and drag up or down in order to select many continuous fields and proceed with next procedure (item below); 
* choose field(s) from `Fields available` list and use the button with left arrow icon (|questionnaire_left_arrow_export|) to transfer them to the `Fields chosen` list. You can choose more than one field by clicking and holding the control(Windows/Linux)/command(Mac) key many times;
* click the left double arrow (|questionnaire_double_left_arrow_export|) to transfer all fields from `Fields available` list to `Fields chosen` list; 

.. |questionnaire_left_arrow_export| image:: ../../_img/questionnaire_left_arrow_export.png

.. |questionnaire_double_left_arrow_export| image:: ../../_img/questionnaire_double_left_arrow_export.png

.. image:: ../../_img/questionnaire_selecting_fields_export.png

At the same way, you can use right arrow (|questionnaire_right_arrow_export|) and right double arrow (|questionnaire_double_right_arrow_export|) to transfer fields from `Fields chosen` list to  `Fields available` list. You can also select fields from `Fields chosen` list using the same mechanism presented above.

.. |questionnaire_right_arrow_export| image:: ../../_img/questionnaire_right_arrow_export.png

.. |questionnaire_double_right_arrow_export| image:: ../../_img/questionnaire_double_right_arrow_export.png 

As soon as a new element is inserted/deleted from the `Fields chosen` list, the blue counter (|questionnaire_fields_counter_export|) updates its value. 

.. |questionnaire_fields_counter_export| image:: ../../_img/questionnaire_fields_counter_export.png

.. _participants-export-participant:

Participants
------------

.. image:: ../../_img/participants_export.png

At the `Participants` section, you can select one or more participants fields to be exported. You can use the following procedures to select the fields:

* click one field and drag up or down in order to select many continuous fields;
* choose more than one field by holding the control(Windows/Linux)/command(Mac) key and clicking each field. You can also unselect the field by clicking a selected field once more while holding control(Windows/Linux)/command(Mac) key.

Please pay attention to not to press and release keys, or the selection may be lost and you have to restart it.

Not all participants fields are available, because there is a concern about data anonymization. 

.. _diagnosis-export-participant:

Diagnosis
---------

.. image:: ../../_img/diagnosis_export.png

The same procedure used with Participants list should be used in the Diagnosis list.

.. _executing-a-export-export-participant:

Executing a export
------------------

After selecting fields to be exported, click `Run` button in order to start the process. A zipped file will be generated and downloaded to your machine. This zipped file can contain one or more csv files.

You can also click `Cancel` button to cancel the export process (only if the process of exportation hasn't been started yet).

.. image:: ../../_img/run_cancel_export.png

:ref:`Back to Export <export>`
