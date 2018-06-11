.. _permissions:

Permissions
===========

NES determines what you are allowed to do in it by looking at the permissions you have.

.. _list-of-permissions-used-by-nes:

List of permissions used by NES
-------------------------------

A permission is a binary (yes/no) flag designating whether you may perform a certain task. Here is the list of permissions that NES checks while you use the system:

* `Add user`
* `Change user`
* `Delete user`
* `Add participant`
* `Change participant`
* `View participant`
* `Delete participant`
* `Export participant`
* `View sensitive participant data`
* `Add medical record data`
* `View medical record data`
* `Export medical record data`
* `Add questionnaires`
* `Change questionnaires`
* `View lists of questionnaires`
* `Delete questionnaires`
* `Add questionnaire response`
* `Change questionnaire response`
* `View questionnaire response`
* `Delete questionnaire response`
* `Export questionnaire response`
* `Add research project`
* `Change research project`
* `View research project`
* `Delete research project`
* `Add experiment`
* `Change experiment`
* `Delete experiment`
* `Change research project created by others`
* `Register equipment`

.. _group-of-users-roles:

Group of Users / Roles
----------------------
To easily apply permissions to more than one user, the administrator of NES can create groups of users. Using groups, instead of applying individual permissions directly to users, the administrator applies permissions to groups and include users in one or more groups. This way, if the group has a certain permission and a user is in this group, he or she will also have this permission.

In NES, we treat groups of users as roles. Thus, although you may be in more than one group (have more than one role), usually the permissions of a single role will be exactly what you need. The roles we suggest for NES are `Administrator`, `Attendant`, `Physiotherapist`, `Doctor`, `Junior researcher`, and `Senior researcher`. See :ref:`script-for-creating-initial-data` to know the permissions each role has. However, using the :ref:`administration-interface`, the administrator may change the list of roles and the permissions for each role to best suit the needs of the hospital or the research institution.