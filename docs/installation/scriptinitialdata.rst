.. _script-for-creating-initial-data:

Script for creating initial data
================================

After installing NES, all you have in the database is a single user. However, there are some data that all NES databases should have, such as certain groups of users, options related to fields that describe  participants, and stimulus types. To facilitate the process of writing these data into the database, the development team has created a script. Current version of NES offers only a script that creates these data in Portuguese. An English version of the script will be available in the next version of NES. 

.. _initial-data-created-by-the-script:

Initial Data Created by the Script
----------------------------------
The first data created by the script are the groups of users, each having specific :ref:`permissions`. Six groups are created:

Administrator
`````````````
* *Add user*
* *Change user*
* *Delete user*

Attendant
`````````
* *Add participant*
* *Change participant*
* *View participant*
* *Delete participant*

Physiotherapist
```````````````
* Same permissions from an attendant
* *View clinical record data*
* *View lists of questionnaires*
* *Add questionnaires*
* *Change questionnaires*
* *Delete questionnaires*
* *Add entrance questionnaire response*
* *Change entrance questionnaire response*
* *View entrance questionnaire response*
* *Delete entrance questionnaire response*

Doctor
``````
* Same permissions from a physiotherapist
* *Add clinical record data*

Junior researcher
`````````````````
* Same permissions from a physiotherapist
* *Add research project*
* *Change research project*
* *View research project*
* *Delete research project*
* *Add experiment*
* *Change experiment*
* *Delete experiment*
* *Add experiment questionnaire response*
* *Change experiment questionnaire response*
* *View experiment questionnaire response*
* *Delete experiment questionnaire response*
* *Add participant to a group*
* *Change subject of a group*
* *Delete participant from a group*
* *Register equipment*

Senior researcher
`````````````````
* Same permissions from a junior researcher
* *Change research project belonging to others*
* *Export participant*
* *Export medical record*
* *Export entrance questionnaire response*
* *View sensitive participant data*

Then, the script creates options related to fields that describe a participant. This is done for 9 sets of options:

**Alcohol consumption frequency**

* Every day
* Every weekend
* Sporadically

**Alcohol consumption period**

* More than 10 years
* 5-10 years
* 1-5 years
* Less than 1 year

**Amount of cigarettes**

* More than 3 packs
* 1-2 packs
* Less than 1 pack

**Skin color**

* Yellow
* White
* Indigenous
* Brown
* Black

**Gender**

* Male
* Female

**Marital status**

* Not informed
* Widower
* Separated/Divorced
* Married/Live together
* Single

**Payment**

* Private
* Health insurance
* Brazilian public health care system

**Religion**

* Buddhism
* Candomblé
* Catholic
* Spiritist
* Evangelical
* The Church of Jesus Christ of Latter-day Saints
* Judaism
* Protestant
* Oriental religions
* No religion
* Jehovah's Witness
* Umbanda

**Education**

* Graduated
* Finished high school
* Finished secondary school
* Finished primary school
* Illiterate / Did not finished primary school

Finally, the script create **stimulus types**

* Auditory
* Gustative
* Interoceptive
* Olfactory
* Somatosensory
* Visual

.. _running-the-script:

Running the Script
------------------
To run the script, you have to run the following commands.

#. Enter the folder where the script is located::

    cd [folder where NES is installed]/patientregistrationsystem/qdc

#. Give execution permission to the script::

    chmod +x add_initial_data.py

#. Execute the script::

    python manage.py shell < add_initial_data.py