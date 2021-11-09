.. _how-to-run-the-unit-tests-of-nes:

How to run the unit tests of NES
=============================================
In this guide, we will demonstrate how to run the unit tests of NES. 


.. Note::
  * We will assume NES was installed according to the :ref:`tutorial-to-install-the-latest-version-of-nes`.
  * For demonstration purposes, we assume NES was deployed at ``/usr/local/nes-system``.


.. running-tests:

Running the tests
-----------------

1. In order to execute the tests, the NES user in PostgreSQL must have permission to create databases. Grant permission to create databases for the NES user in PostgreSQL  (change ``nes`` for NES database user name)::

    sudo su postgres -c 'psql'

    alter role nes with createdb;

    quit;

2. Activate virtualenv::

    cd /usr/local/nes-system/

    source bin/activate

Next steps will be executed inside the virtualenv.

3. Change path to::

    cd /usr/local/nes-system/nes/patientregistrationsystem/qdc

4. Run the tests::

    python manage.py test

