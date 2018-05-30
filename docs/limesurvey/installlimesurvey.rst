.. _how-to-install-limesurvey:

How to install LimeSurvey
=========================

.. _tutorial-to-install-the-latest-version-of-limesurvey:

Tutorial to install the latest version of LimeSurvey
----------------------------------------------------

In this guide, we will demonstrate how to install and configure LimeSurvey. We'll assume that you already have a server with Apache and PostgreSQL installed (If you installed NES, then you have it!).

.. _important-technical-information:

Important technical information
```````````````````````````````
* This guide walks through an installation by using packages available through Debian 9 (code name: Stretch), but can easily be adapted to other Unix operating systems.
* For demonstration purposes, we will use the ``/var/www`` directory to deploy the LimeSurvey.
* Always check the `official LimeSurvey manual <https://manual.limesurvey.org/>`_ for the most up-to-date information!

.. _initial-setup-limesurvey:

Initial setup
`````````````
1. Before running through the steps of this tutorial, make sure that all of your repositories are up to date::

    apt-get update

2. Install some packages::

    apt-get install php php-pgsql php-gd php-imap php-mbstring php-ldap php-zip php-xml

3. Check the latest version of LimeSurvey `here <https://www.limesurvey.org/stable-release>`_ and download the file with the `tar.gz` extension. 

4. Extract the file (rename the file according to what you've downloaded)::

    tar xzvf limesurvey2_X.X.tar.gz

    rm limesurvey2_X.X.tar.gz

5. Change owner and group::

    chown -R www-data.www-data limesurvey/

6. Change directory permissions::

    chmod -R o-rwx limesurvey/

    chmod -R 770 limesurvey/application/config/

    chmod -R 770 limesurvey/upload/

    chmod -R 770 limesurvey/tmp/
 
7. Create user and database (you will use this user/password/database soon)::

    su - postgres

    createuser limesurvey --pwprompt --encrypted

    createdb limesurvey --owner=limesurvey

    exit

8. Create a virtual host::

    nano /etc/apache2/sites-available/limesurvey.conf

Insert the following content, but remembering that the paths and the ServerName provided should be changed according to your installation::

    <VirtualHost *:80>
  	ServerName limesurvey.example.com

    	DocumentRoot /var/www/limesurvey

    	<Directory />
    	    	Options FollowSymLinks
    	    	AllowOverride None
    	</Directory>

    	<Directory /var/www/limesurvey>
    	    	Options Indexes FollowSymLinks MultiViews
    	    	AllowOverride None
    	    	Order allow,deny
    	    	allow from all
    	    	AcceptPathInfo On
    	</Directory>

    	ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/

    	<Directory "/usr/lib/cgi-bin">
    	    	AllowOverride None
    	    	Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
    	    	Order allow,deny
    	    	Allow from all
    	</Directory>

    	ErrorLog ${APACHE_LOG_DIR}/limesurvey_ssl_error.log
    	LogLevel warn
    	CustomLog ${APACHE_LOG_DIR}/limesurvey_ssl_access.log combined
    </VirtualHost>

9. Enable the virtual host::

    a2ensite limesurvey

    systemctl reload apache2

10. Web-based configuration

Using a browser, access the server using the IP address of the machine or its name and complete the installation. At this step you will:

* Select the language to be used
* You have to agree with the license
* See if you have all the packages needed installed
* Set the database (using the credentials of step 7)
* Create and populate the database 
* Create an administrator user

