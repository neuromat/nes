# NES/Limesurvey Docker Compose

Docker-compose to build a [NES](https://github.com/neuromat/nes) installation integrated with [PostgreSQL](https://www.postgresql.org) and [LimeSurvey](https://limesurvey.org).

<!---
Parts of this README file are based on Markus Opolka work with the following license:

MIT License

Copyright (c) 2018 Markus Opolka

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
--->

# Postgres Configuration

This docker image was kept as close of the original as possible, so all of its configuration based strictly on environment variables.

## Environment Variables

| Parameter         | Description                           |
| ----------------- | ------------------------------------- |
| POSTGRES_DB       | Postgres initial database             |
| POSTGRES_USER     | Postgres initial (super) user         |
| POSTGRES_PASSWORD | Postgres initial (superuser) password |

For further details on the settings see: <https://hub.docker.com/_/postgres>

# LimeSurvey Configuration

The entrypoint will create a new config.php if none is provided and run the LimeSurvey command line interface for installation.

**Hint**: If this configuration is present before the installation, the LimeSurvey Web Installer will not run automatically.

## Build Arguments

| Parameter               | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| LIMESURVEY_URL_DOWNLOAD | URL to be used to install a specific LimeSurvey version |
| LIMESURVEY_DIR          | Directory where LimeSurvey will be installed            |

## Environment Variables

| Parameter                  | Description                           |
| -------------------------- | ------------------------------------- |
| LIMESURVEY_PORT            | LimeSurvey port to be used by Apache. |
| LIMESURVEY_DB_TYPE         | Database Type to use. mysql or pgsql  |
| LIMESURVEY_DB_HOST         | Database server hostname              |
| LIMESURVEY_DB_PORT         | Database server port                  |
| LIMESURVEY_DB_NAME         | Database name                         |
| LIMESURVEY_DB_TABLE_PREFIX | Database table prefix                 |
| LIMESURVEY_DB_USERNAME     | Database user                         |
| LIMESURVEY_DB_PASSWORD     | Database user's password              |
| LIMESURVEY_ADMIN_USER      | LimeSurvey Admin User                 |
| LIMESURVEY_ADMIN_NAME      | LimeSurvey Admin Username             |
| LIMESURVEY_ADMIN_EMAIL     | LimeSurvey Admin Email                |
| LIMESURVEY_ADMIN_PASSWORD  | LimeSurvey Admin Password             |
| LIMESURVEY_PUBLIC_URL      | Public URL for public scripts         |
| LIMESURVEY_URL_FORMAT      | URL Format. path or get               |

For further details on the settings see: <https://manual.limesurvey.org/Optional_settings#Advanced_Path_Settings>

# NES Configuration

The entrypoint will set the required application settings and run the initial scripts to populate the database and to be sure to run those only at the first run, a placeholder is written at '/var/tmp/nes_is_configured'

## Build Arguments

| Parameter  | Description                           |
| ---------- | ------------------------------------- |
| NES_TAG    | NES release tag to be installed       |
| NES_BRANCH | NES git branch to be installed        |
| NES_DIR    | Directory where NES will be installed |

## Environment Variables

| Parameter                 | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| NES_DB_TYPE               | Database type to use. For now, only works with pgsql |
| NES_DB_HOST               | Database server hostname                             |
| NES_DB_PORT               | Database server port                                 |
| NES_DB                    | Database name                                        |
| NES_DB_USER               | Database user                                        |
| NES_DB_PASSWORD           | Database user's password                             |
| LIMESURVEY_HOST           | LimeSurvey server hostname                           |
| LIMESURVEY_PORT           | LimeSurvey server port                               |
| LIMESURVEY_ADMIN_USER     | LimeSurvey Admin User                                |
| LIMESURVEY_ADMIN_PASSWORD | LimeSurvey Admin Password                            |
| NES_SECRET_KEY            | NES Secret Key for Django deployment                 |
| NES_IP                    | NES IP address to be user by Django                  |
| NES_PORT                  | NES port to be used by Django                        |
| NES_ADMIN_USER            | NES Admin User                                       |
| NES_ADMIN_EMAIL           | NES Admin Email                                      |
| NES_ADMIN_PASSWORD        | NES Admin Password                                   |

# References

-   <https://github.com/LimeSurvey/LimeSurvey/>
-   <https://github.com/martialblog/docker-limesurvey>
-   <https://github.com/gliderlabs/docker-alpine>
-   <https://github.com/docker-library/httpd>
-   <https://github.com/docker-library/postgres>
