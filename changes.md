updated to python 3.11
updated to Django 4.2
updated boostrap, jquery and jquery-ui
added django-axes to prevent bruteforce login 
renamed quiz/static/quiz to quiz/static/data to better refelct its functionality

improved project structure:
https://studygyaan.com/django/best-practice-to-structure-django-project-directories-and-files
https://django-project-skeleton.readthedocs.io/en/latest/structure.html
    removed quiz folder
    added site_static folder for all the site's .html, .css, .js and images
    moved quiz/templates to /templates
    added a base template to registration html
    added a modular settings system

improved deploy


TODO:

update to boostrap 4 or 5
update to jquery 3 or remove jquery
finish portuguese translation
change nwb(deprecated) to pynwb