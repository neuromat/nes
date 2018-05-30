.. _studies:

Studies
===========
NES offers the possibility of creating studies.

List of Studies
---------------
To access the list of studies already registered in the system, click on the `Study` menu item. This screen allows the creation of a new study or the visualization of an existing study.

.. image:: ../_img/studies_list.png

Creating and Editing a Study
----------------------------
A study contains:

* A title (obligatory);
* A description (obligatory);
* A start date (obligatory);
* An end date;
* A list of keywords;
* A list of colaborators;
* A list of experiments; and
* An owner (obligatory).

However, while creating a new study, the screen asks only for the title, description, and term of a study. Those are also the fields that can be updated if you click the `Edit` button in the visualization screen. Keywords and experiments can be added while visualizing a study. During creation, the logged user becomes the owner of the study. The owner cannot be changed. Only authorized users can update a study, which means the owner of the study or users with permission to change the study (See :ref:`permissions` for more information).

.. image:: ../_img/studies_edit.png

Visualizing a Study
-------------------
You can see more information about an existing study by clicking on its title in the list of studies. While viewing a study, you can delete it by clicking the `Delete` button. However, this button is visible only for the users that have permission to update a study.

.. image:: ../_img/studies_visualizing.png

Keywords of a study
-------------------
You can manage keywords while viewing the information about a study. To add a new keyword, simply type the desired keyword in the text field on the `Keywords` section. The system suggests keywords already in use by other studies that are still not in use in the current study, or the creation of a new one. You should then select one of the options from the list. It is not possible to include more than one keyword at the same time. To remove a keyword, simply click the :x: button associated to it. Again, only users that have permission to update a study can add or remove keywords. Non-authorized users can't see the text field.

.. image:: ../_img/keywords_view.png

Experiments of a study
----------------------
A study may have multiple :ref:`experiments`. Again, only users that have :ref:`permissions` to update a study can add experiments. Non-authorized users can't see the `Insert new` button.

.. image:: ../_img/experiment_view.png
