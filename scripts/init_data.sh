#!/bin/sh

# INITIALIZE DATA ####################################################

## PG DB
# if [ -f "${PGDATA}"/.db_users.placeholder ]; then
# 	echo "INFO: DB users already provisioned"
# else
# 	echo "INFO: Creating users in postgres"
# 	cd /
# 	su postgres -c "psql start -w -D $PGDATA"
# 	cat <<-EOF | su postgres -c "psql"
# 		CREATE USER $NES_DB_USER WITH PASSWORD "$NES_DB_PASSWORD" ;
# 		CREATE DATABASE $NES_DB OWNER $NES_DB_USER ;
# 		GRANT ALL PRIVILEGES ON DATABASE $NES_DB TO $NES_DB_USER ;
# 		ALTER ROLE $NES_DB_USER WITH CREATEDB;
# 		CREATE USER $LIMESURVEY_DB_USER WITH PASSWORD "$LIMESURVEY_DB_PASSWORD" ;
# 		CREATE DATABASE $LIMESURVEY_DB_NAME OWNER $LIMESURVEY_DB_USER ;
# 		GRANT ALL PRIVILEGES ON DATABASE $LIMESURVEY_DB_NAME TO $LIMESURVEY_DB_USER ;
# 	EOF
# 	su postgres -c "psql stop -w -D $PGDATA"
# 	touch "${PGDATA}"/.db_users.placeholder
# fi

## NES
if [ -f "$NES_DIR"/.nes_initialization.placeholder ]; then
    echo "INFO: NES data has already been initialized"
else
    echo "INFO: Initializing NES data (migrations, initial, superuser, ICD)"
    cd ../patientregistrationsystem/qdc/
    
	cat <<-EOF >/tmp/create_superuser.py
		from django.contrib.auth import get_user_model
		User = get_user_model()
		User.objects.create_superuser("$NES_ADMIN_USER", "$NES_ADMIN_EMAIL", "$NES_ADMIN_PASSWORD")
	EOF
    
    echo "	INFO: Migrate"
    python3 -u manage.py migrate
    # Different versions may have different commands
    echo "	INFO: add_initial_data.py"
    python3 -u manage.py shell < add_initial_data.py || true
    echo "	INFO: load_initial_data.py"
    python3 -u manage.py loaddata load_initial_data.json || true
    echo "	INFO: create_super_ser.py"
    python3 -u manage.py shell < /tmp/create_superuser.py || true
    echo "	INFO: import cid10"
    python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true
    echo "	INFO: createcachetable"
    python3 -u manage.py createcachetable || true
    
    rm /tmp/create_superuser.py
    
    # If NES was installed from a release it won"t have a .git directory
    chown -R nobody "${NES_DIR}"/.git || true
    chown -R nobody "${NES_DIR}"/patientregistrationsystem
    
    touch "$NES_DIR"/.nes_initialization.placeholder
fi

echo "Done"