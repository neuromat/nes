.. _guidelines-to-integrate-nes-and-limesurvey:

Guidelines to Integrate NES and LimeSurvey
==========================================

After the installation of both NES and LimeSurvey, there are some specific steps that have to be done before you can use them together, as explained below.

1. Change the ``settings_local.py`` file. If you followed the installation steps as described :ref:`here <tutorial-to-install-the-latest-version-of-nes>`, this file should be in ``/usr/local/nes-system/nes/patientregistrationsystem/qdc/qdc/settings_local.py``.

   Open the ``settings_local.py`` file and edit the lines about LimeSurvey. You need to use a user with administrative privileges here::

        # LimeSurvey configuration
        LIMESURVEY = { 
            'URL_API': 'http://example.limesurvey.server.com',
            'URL_WEB': 'http://example.limesurvey.server.com',
            'USER': 'limesurvey_admin_user',
            'PASSWORD': 'limesurvey_password'
        }

2. Change LimeSurvey settings.

   Log in as administrator at LimeSurvey/admin page.

   Go to LimeSurvey and in ``Global Settings`` and then ``Interfaces`` tab and at the ``RPC interface enabled`` option, change to ``JSON-RPC`` and click the ``save settings`` button.

.. image:: ../_img/global_settings.png


3. Check if your integration settings are working.

Click on the Questionnaires link in the NES system menu, if everything is correct, you can already insert questionnaires, otherwise you will see an alert saying `"LimeSurvey unavailable. System running partially"`.

If you already have a questionnaire included in LimeSurvey, you can go to :ref:`questionnaires` to see how to use it.

Remember to verify if conditions presented in :ref:`how-to-integrate-nes-and-limesurvey-questionnaire` page are correctly set up.