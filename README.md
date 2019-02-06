# NES/Limesurvey Docker

Dockerfile to build a monolithic container of [NES](https://github.com/neuromat/nes) with [PostgreSQL](https://www.postgresql.org) and [LimeSurvey](https://limesurvey.org).

# Environment variables
The environment variables can be organized in the following groups:

## PostgreSQL
| Parameter | Description |
| --------- | ------------ |
| PGDATA | Directory where PostgreSQL stores its files |

## LIMESURVEY
### SYSTEM OPTIONS
| Parameter | Description |
| --------- | ------------ |
| LIMESURVEY_HOST | Host where LimeSurvey is installed. (default is localhost) |
| LIMESURVEY_PORT | LimeSurvey port to be used by Apache. |
| LIMESURVEY_URL_DOWNLOAD | URL used to download a specific LimeSurvey version. |
| LIMESURVEY_DIR | Directory where LimeSurvey will be installed. |
| LIMESURVEY_CONF_DIR | Directory where Apache settings will be stored. |

### CONFIG.PHP OPTIONS
| Parameter | Description |
| --------- | ------------ |
| LIMESURVEY_DB_HOST | Database server hostname. (default is localhost) |
| LIMESURVEY_DB_PORT | Database server port. |
| LIMESURVEY_DB | Database name. |
| LIMESURVEY_DB_TABLE_PREFIX | Database table prefix. |
| LIMESURVEY_DB_USER | Database user. |
| LIMESURVEY_DB_PASSWORD | Database password. |
| LIMESURVEY_DB_CHARSET | Database charset to be used. |
| LIMESURVEY_URL_FORMAT | URL Format. path or get. |

### SUPER USER CREATION OPTION
| Parameter | Description |
| --------- | ------------ |
| LIMESURVEY_ADMIN_USER | LimeSurvey Admin User. |
| LIMESURVEY_ADMIN_NAME | LimeSurvey Admin Username. |
| LIMESURVEY_ADMIN_EMAIL | LimeSurvey Admin Email. |
| LIMESURVEY_ADMIN_PASSWORD | LimeSurvey Admin Password. |

## NES

### SYSTEM OPTIONS
| Parameter | Description |
| --------- | ------------ |
| NES_DIR | Directory where NES will be installed. |
| NES_TAG | NES tag version to be installed. |
| NES_PROJECT_PATH | Subdirectory where the NES project is located. |
| NES_SETUP_PATH | Subdirectory where the NES settings are located. |

### SETTINGS_LOCAL OPTIONS

#### DJANGO
| Parameter | Description |
| --------- | ------------ |
| NES_SECRET_KEY | NES Secret Key for Django deployment. |
| NES_ADMIN_USER | NES Admin User. |
| NES_ADMIN_EMAIL | NES Admin Email. |
| NES_ADMIN_PASSWORD | NES Admin Password. |
| NES_IP | NES IP address to be user by Django. |
| NES_PORT | NES port to be user by Django. |

#### DB
| Parameter | Description |
| --------- | ------------ |
| NES_DB_TYPE | Database type to use. For now, only works with pgsql. |
| NES_DB_HOST | Database server hostname. (default is localhost) |
| NES_DB | Database name. |
| NES_DB_PORT | Database server port. |
| NES_DB_USER | Database user. |
| NES_DB_PASSWORD | Database user's password. |

#### LimeSurvey JSON-RPC interface
*these are the same variables set for LimeSurvey*

| Parameter | Description |
| --------- | ------------ |
| LIMESURVEY_HOST | Host where LimeSurvey is installed. (default is localhost) |
| LIMESURVEY_PORT | LimeSurvey port to be used by Apache. |
| LIMESURVEY_ADMIN_USER | LimeSurvey Admin User. |
| LIMESURVEY_ADMIN_PASSWORD | LimeSurvey Admin Password. |

# References

- https://github.com/LimeSurvey/LimeSurvey/
- https://github.com/martialblog/docker-limesurvey
- https://github.com/gliderlabs/docker-alpine
- https://github.com/docker-library/httpd
- https://github.com/docker-library/postgres

# TO-DO
- [X] Split the database in two, each serving a different system (nes/limesurvey);
- [ ] :warning: Load ICD data :warning:;
- [ ] Integrate this repo with the DockerHub for continuous integration;
- [ ] Make a deploy version with NES on Apache setup;
- [ ] Make the actual template a test version;
- [ ] Make NES deployable with different SQL databases and integrate it with docker;
- [ ] Make different deploy templates with other webserver (nginx);
