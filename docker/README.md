# NES/LimeSurvey Docker

Dockerfile to build a monolithic container of [NES](https://github.com/neuromat/nes) with [PostgreSQL](https://www.postgresql.org) and [LimeSurvey](https://limesurvey.org).

The integration and deployment of the services is handled by [Supervisor](http://supervisord.org/).

# Build Arguments

The build arguments can be organized in the following groups:

## PostgreSQL

| Parameter | Description                                 |
| --------- | ------------------------------------------- |
| PGDATA    | Directory where PostgreSQL stores its files |

## LimeSurvey

| Parameter               | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| LIMESURVEY_URL_DOWNLOAD | URL to be used to install a specific LimeSurvey version |
| LIMESURVEY_DIR          | Directory where LimeSurvey will be installed            |

## NES

| Parameter  | Description                           |
| ---------- | ------------------------------------- |
| NES_TAG    | NES release tag to be installed       |
| NES_BRANCH | NES git branch to be installed        |
| NES_DIR    | Directory where NES will be installed |

# Environment variables

The environment variables can be organized in the following groups:

## PostgreSQL

| Parameter | Description                                 |
| --------- | ------------------------------------------- |
| PGDATA    | Directory where PostgreSQL stores its files |

## LimeSurvey

### SYSTEM OPTIONS

| Parameter       | Description                                                |
| --------------- | ---------------------------------------------------------- |
| LIMESURVEY_HOST | Host where LimeSurvey is installed. (default is localhost) |
| LIMESURVEY_PORT | LimeSurvey port to be used by Apache.                      |

### CONFIG.PHP OPTIONS

| Parameter                  | Description                                      |
| -------------------------- | ------------------------------------------------ |
| LIMESURVEY_DB_HOST         | Database server hostname. (default is localhost) |
| LIMESURVEY_DB_PORT         | Database server port.                            |
| LIMESURVEY_DB_NAME              | Database name.                                   |
| LIMESURVEY_DB_TABLE_PREFIX | Database table prefix.                           |
| LIMESURVEY_DB_USER         | Database user.                                   |
| LIMESURVEY_DB_PASSWORD     | Database password.                               |
| LIMESURVEY_DB_CHARSET      | Database charset to be used.                     |
| LIMESURVEY_URL_FORMAT      | URL Format. path or get.                         |

### SUPER USER CREATION OPTION

| Parameter                 | Description                |
| ------------------------- | -------------------------- |
| LIMESURVEY_ADMIN_USER     | LimeSurvey Admin User.     |
| LIMESURVEY_ADMIN_NAME     | LimeSurvey Admin Username. |
| LIMESURVEY_ADMIN_EMAIL    | LimeSurvey Admin Email.    |
| LIMESURVEY_ADMIN_PASSWORD | LimeSurvey Admin Password. |

## NES

### SETTINGS_LOCAL OPTIONS

#### DJANGO

| Parameter          | Description                           |
| ------------------ | ------------------------------------- |
| NES_SECRET_KEY     | NES Secret Key for Django deployment. |
| NES_ADMIN_USER     | NES Admin User.                       |
| NES_ADMIN_EMAIL    | NES Admin Email.                      |
| NES_ADMIN_PASSWORD | NES Admin Password.                   |
| NES_IP             | NES IP address to be user by Django.  |
| NES_PORT           | NES port to be user by Django.        |

#### DB

| Parameter       | Description                                      |
| --------------- | ------------------------------------------------ |
| NES_DB_HOST     | Database server hostname. (default is localhost) |
| NES_DB          | Database name.                                   |
| NES_DB_PORT     | Database server port.                            |
| NES_DB_USER     | Database user.                                   |
| NES_DB_PASSWORD | Database user's password.                        |

#### LimeSurvey JSON-RPC interface

_these are the same variables set for LimeSurvey_

| Parameter                 | Description                                                |
| ------------------------- | ---------------------------------------------------------- |
| LIMESURVEY_HOST           | Host where LimeSurvey is installed. (default is localhost) |
| LIMESURVEY_PORT           | LimeSurvey port to be used by Apache.                      |
| LIMESURVEY_ADMIN_USER     | LimeSurvey Admin User.                                     |
| LIMESURVEY_ADMIN_PASSWORD | LimeSurvey Admin Password.                                 |

## Supervisor

| Parameter           | Description                                        |
| ------------------- | -------------------------------------------------- |
| SUPERVISOR_CONF_DIR | Directory where Supervisor configuration is stored |

# References

-   https://github.com/LimeSurvey/LimeSurvey/
-   https://github.com/martialblog/docker-limesurvey
-   https://github.com/gliderlabs/docker-alpine
-   https://github.com/docker-library/httpd
-   https://github.com/docker-library/postgres

# TO-DO

-   [x] Split the database in two, each serving a different system (nes/limesurvey);
-   [x] :warning: Load ICD data :warning:;
-   [x] Integrate this repo with the DockerHub for continuous integration;
-   [ ] Make a deploy version with NES on Apache setup;
-   [ ] Make the actual template a test version;
-   [ ] Make NES deployable with different SQL databases and integrate it with docker;
-   [ ] Make different deploy templates with other webserver (nginx);
