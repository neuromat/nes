.. _personal-data:

Personal Data
=============

Personal data is the tab where you can view or update participant's basic information, address and telephone numbers.

Personal Data Tab
-----------------
You can visit the :ref:`participants` page to understand how to navigate between tabs.

.. image:: ../../_img/participant_personal_data.png

Basic Information
`````````````````

In this section, you can visualize/edit participant's basic information:

* Full name (obligatory);
* CPF (not obligatory, but recommended);
* Origin;
* Medical record;
* Date of birth (obligatory);
* Gender (obligatory);
* ID; and
* Marital status.

.. note:: The `Cadastro de Pessoas Físicas` (CPF) is a number attributed by the Brazilian Federal Revenue to both Brazilians and resident aliens, which is widely used as an identification number in Brazil.

Once the CPF number is unique for each person, it is very important when one is trying to verify `Participant Homonym`_. If you don't fill in this information, a confirmation message will show up, but you can just ignore if it is not an important information for you (click either the `Save` button if you want to continue the saving process without CPF or the `Cancel` button if you'd rather go back and inform the CPF number).

.. image:: ../../_img/participant_cpf_not_filled.png

Address 
```````

The address section contains (all information is optional):

* Country;
* Zip code;
* Address;
* Number;
* Complement;
* District;
* City;
* State; and
* E-mail.

.. image:: ../../_img/participant_address.png

The zip code field has a mask that forces the field to accept only numbers with 8 digits. This is the format used in Brazil. Zip code of future versions will have this mask only if you choose Brazil as the country.

Telephones
``````````

The telephones section contains:

* Number;
* Type;
* Observation; and
* Delete - it is possible to delete specific telephones.

.. image:: ../../_img/participant_phone.png

You have to click the `Save and include more telephones` button (:ref:`only in edition mode <creating-and-editing-a-participant>`) if you need more room for entering new telephones. If you want to delete one telephone number, mark the delete box of it and click this button as well.

.. _participant-homonym:

Participant Homonym
```````````````````

When you create a new participant, NES searches for homonyms by the full name or the CPF number that was previously registered in the system.

If this occurs, an warning message is presented:

.. image:: ../../_img/participant_homonym.png

You can either continue inserting a new participant (click `Cancel` button) or click the participant's CPF-name link to view the registered one.