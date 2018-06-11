.. _how-to-integrate-nes-and-limesurvey-questionnaire:

How to Integrate NES and LimeSurvey Questionnaire
=================================================

A questionnaire created in LimeSurvey can only be used on the NES system if it has certain properties, defined at the creation and activation times of the questionnaire. These properties are:

* The questionnaire must have `Token-based response persistence`_
* The questionnaire must have a `Group of Hidden Questions Called NESIdentification`_
* The questionnaire must use `Token-based access control`_

To assign these three properties to a questionnaire, follow the instructions presented in the following sections.

.. _token-based-response-persistence:

Token-based response persistence
--------------------------------
.. image:: ../_img/limesurvey_edit.png

* Open the questionnaire for editing in LimeSurvey (``Survey Properties|Edit text elements``)

.. image:: ../_img/limesurvey_general_settings.png

* Enter ``General Settings` menu, and then ``Tokens`` tab 

.. image:: ../_img/limesurvey_enable_token.png

* Choose ``Yes`` to option ``Enable token-based response persistence?``
* Click the ``Save`` button at the bottom of page.

.. _group-of-hidden-questions-called-nesidentification:

Group of Hidden Questions Called ``NESIdentification``
------------------------------------------------------

This group must contain three questions with the codes and types defined in the following:

* Participant Identification number → question code: ``subjectid``; question type: ``numerical input``;
* Responsible Identification number → question code: ``responsibleid``; question type: ``numerical input``;
* Acquisition date → question code: ``acquisitiondate``; question type: ``date/time``.

You can easily include this group of questions in a questionnaire through the functionality of `Group Import` available in LimeSurvey. To import the ``NESIdentification` group to a questionnaire, follow these steps:

* Download the file `NESIdentification.lsg <https://raw.githubusercontent.com/neuromat/nes/DEV-0.2.1/resources/NESIdentification.lsg>`_;

* Open the questionnaire for editing in LimeSurvey (``Survey Properties|Edit text elements``);

.. image:: ../_img/limesurvey_add_new_group.png

* Enter ``Add new group to survey`` menu and then ``Import question group`` tab;

.. image:: ../_img/limesurvey_import_question_group.png

* At the ``Select question group file (*.lsg)`` field, select ``NESIdentification.lsg`` file downloaded before;
* Click the ``Import question group`` button at the bottom of the page.

.. _token-based-access-control:

Token-based access control
--------------------------
* For a questionnaire that has been activated:
* Open the questionnaire for editing in LimeSurvey (``Survey Properties|General Settings``)

.. image:: ../_img/limesurvey_token_management.png

* Enter the "Token management" menu and then click the ``Initialise tokens`` button;

.. image:: ../_img/limesurvey_initialise_tokens.png

* On the next screen, click the ``Continue`` button;

.. image:: ../_img/limesurvey_continue.png


* For a questionnaire that has not been activated yet, the use of tokens to control the access to the questionnaire can be enabled when the questionnaire is activated:

.. image:: ../_img/limesurvey_activate_survey.png

* After the questionnaire is ready for use, enter the ``Activate this Survey`` menu and then click the ``Save / Activate survey`` button

.. image:: ../_img/limesurvey_save_activate_survey.png

* On the next screen, click the ``Switch to closed-access mode`` button

.. image:: ../_img/limesurvey_switch_closed_access_mode.png

* On the next screen, click the ``Initialise tokens`` button

.. image:: ../_img/limesurvey_initialise_tokens.png

* On the next screen, click the ``Continue`` button

.. image:: ../_img/limesurvey_continue.png