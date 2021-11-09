.. _loading-icd-data-3.0:

Loading ICD data (3.0)
======================

In order to load ICD (International Code Diseases) data, you will have to pay attention to different languages. In this version, only Portuguese and English versions can be installed. 
The last version of the ICD file was obtained from the `Centro de Terminologias Clínicas (CTC) <https://interop-pt.atlassian.net/wiki/spaces/CTCPT/pages/58884241/Implementa+o+da+ICD-10-CM+PCS>`_.

.. _before-loading-icd-data:

Before loading ICD data
-----------------------

Before loading ICD, you have to guarantee that all migrations have been applied. First of all, 

Activate virtualenv::

    cd /usr/local/nes-system/
    
    source bin/activate

Change path to::
 
    cd /usr/local/nes-system/nes/patientregistrationsystem/qdc

Update migrations::

    python manage.py migrate


Deactivate virtualenv::

    deactivate

.. _loading-icd-data:

Loading ICD data
----------------

Commands to execute steps defined above are::

    cd /usr/local/nes-system/nes/resources/load-idc-table/


Verify that the file exists::

    icd10cid10v2017.csv


Activate virtualenv::

    cd /usr/local/nes-system/
    
    source bin/activate

Change path to::
 
    cd /usr/local/nes-system/nes/patientregistrationsystem/qdc

Update translation data::

    python manage.py import_icd_cid --file icd10cid10v2017.csv


Deactivate virtualenv::

    deactivate
    
