.. qdc documentation master file, created by
   sphinx-quickstart on Fri May 18 13:06:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

NeuroMat Neuroscience Experiments System (NES)
==============================================
`NeuroMat <http://neuromat.numec.prp.usp.br>`_ presents the Neuroscience Experiments System (NES), a software to manage data from neuroscience experiments. NES is a web­based system developed within the NeuroMat project  that provides facilities to record data and metadata from each step of a neuroscience experiment in a secure and user friendly platform. It was developed to assist researchers in their data collecting routine throughout a neuroscience experiment, integrating data records from different types such as clinical, electrophysiological, imaging, and behavioral. Furthermore, it provides a unified repository (database) for the experimental data of an entire research laboratory, group, or project. Its web interface and modular format provide an intuitive use of its data management functionalities. Its use does not depend on any specific knowledge on informatics.

Features
--------
- NES allows to register the experimental protocol in a textual format.
- Various type of experiment data and metadata can be stored at each step of the experimental protocol.
- This NES database is not public use. NES is installed in a laboratory computer machine that is controlled and managed by the laboratory.
- NES allows to export all data and metadata of the experiments which it stores. 
- Any experiment registered in NES can be sent to NeuroMat Open Database to be made publicly available.

Integration with the NeuroMat Open Database
-------------------------------------------
Installations of NES can send experiment data to the NeuroMat Open Database where the experiments will be made publicly available.
Through NES, a researcher will be able to send the data and metadata	 of his/her experiments to the NeuroMat Open Database.  
The data is anonymized before being sent from NES to the Open Database; no sensitive data leaves NES or is stored in the Open Database. When a new dataset of an experiment arrives at the Open Database, it will be evaluated by a curatorial committee. The committee will analyze if the dataset is appropriate for publication on the NeuroMat Open Database. The researcher will be notified of the status of his/her data submission. After approval, the dataset will be made publicly available on the NeuroMat Open Database web portal.
Researchers that don’t have NES installation can send the data and metadata of his/her experiments to the NeuroMat Open Database through REST API. For more information go to `<http://neuromatdb.numec.prp.usp.br/api/docs/>`_.

:ref:`how-to-send-experiment-data-from-nes`

Documentation
-------------
The Research, Innovation and Dissemination Center for Neuromathematics (CEPID NeuroMat) software development team works continually on the development of Neuroscience Experiments System (NES), an open-source tool to organize, control and manage clinical, neurophysiological and experimental data gathered in hospitals and research institutions.

This documentation is divided in 6 parts:

- :ref:`Installation <tutorial-to-install-the-latest-version-of-nes>`

 - :ref:`script-for-creating-initial-data`
 - :ref:`administration-interface`
 - :ref:`loading-icd-data-3.0`
 - :ref:`installation-using-a-docker-container`

- :ref:`limesurvey`

 - :ref:`how-to-install-limesurvey`
 - :ref:`guidelines-to-integrate-nes-and-limesurvey`
 - :ref:`how-to-integrate-nes-and-limesurvey-questionnaire`
 - :ref:`naming-conventions-for-question-codes`

- :ref:`neuromat-open-database`

 - :ref:`how-to-send-experiment-data-from-nes`

- :ref:`userguide`

 - :ref:`participants`

  - :ref:`personal-data`
  - :ref:`social-demographic-data`
  - :ref:`social-history`
  - :ref:`medical-evaluation`
  - :ref:`Questionnaires <participant-questionnaires>`

 - :ref:`studies`

  - :ref:`experiments`

   - :ref:`researchers-of-an-experiment`
   - :ref:`group-of-participants`
   - :ref:`raw-data-and-additional-files`
   - :ref:`recording-settings`
   - :ref:`managing-steps-for-experimental-protocol`
   - :ref:`configuring-an-experimental-protocol`

 - :ref:`publications`
 - :ref:`questionnaires`

  - :ref:`managing-a-questionnaire-fill`
  - :ref:`answering-a-limesurvey-questionnaire`

 - :ref:`researchers`
 - :ref:`set-up`
 - :ref:`export`

  - :ref:`export-participant-data`
  - :ref:`export-experiment-data`

 - :ref:`translation`
 - :ref:`search`
 - :ref:`permissions`
 
- :ref:`For Developers <how-to-run-the-unit-tests-of-nes>`

 - :ref:`how-to-run-the-unit-tests-of-nes`
 
- :ref:`videos`
- :ref:`training`
