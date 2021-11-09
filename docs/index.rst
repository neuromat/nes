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

.. toctree::
   :maxdepth: 1
   :caption: Installation
   :titlesonly:

   installation/installationtutorial
   installation/scriptinitialdata
   installation/admininterface
   installation/icddata3.0
   installation/dockercontainer

.. toctree::
   :maxdepth: 1
   :caption: LimeSurvey
   :titlesonly:

   limesurvey/limesurvey
   limesurvey/installlimesurvey
   limesurvey/guidelines
   limesurvey/integratenesandlimesurvey
   limesurvey/namingconventions
   limesurvey/bestpractices

.. toctree::
   :maxdepth: 1
   :caption: NeuroMat Open Database
   :titlesonly:

   neuromatODb/neuromatodb
   neuromatODb/sendexperimentdata

.. toctree::
   :maxdepth: 1
   :caption: User Guide
   :titlesonly:

   userguide/userguide
   userguide/participants/participants
   userguide/studies
   userguide/publications
   userguide/questionnaires/questionnaires
   userguide/researchers
   userguide/setup/equipmentsetup
   userguide/export/export
   userguide/translation
   userguide/search
   userguide/permissions

.. toctree::
   :maxdepth: 1
   :caption: For Developers
   :titlesonly:
   
   developers/tests

.. toctree::
   :maxdepth: 1
   :caption: Videos
   :titlesonly:

   videos/videos

.. toctree::
   :maxdepth: 1
   :caption: Training
   :titlesonly:

   training/training

