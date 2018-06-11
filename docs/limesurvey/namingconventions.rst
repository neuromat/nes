.. _naming-conventions-for-question-codes:

Naming Conventions for Question Codes
=====================================

This section presents a suggestion on how to name codes that identify questions in LimeSurvey. 

To make it easy the understand and manipulate data collected using questionnaires, we recommend to use a prefix in the code (identifier) of each question. The intention of this prefix is to inform the type of the data "collected" by the question. For example, for a question like "How old are you?", ``intAge`` would be a good code. The ``int`` prefix indicates that the value for the age is an integer number.

The following list contains prefix suggestions for the most frequent types of responses:

* All types of single choice question → ``lst``
* All types of multiple choice questions → ``mul``
* All types of text questions → ``txt``
* Array (Numbers) → ``int`` or ``dec``
* Array (Text) → ``txt``
* Other types of array → ``lst``
* Date/Time → ``dat``
* Equation → ```equ``
* Numerical input → ``int`` or ``dec``
* Multiple numerical input → ``int`` or ``dec``
* Yes/No → ``yn``
* Other types of question → ``txt``
