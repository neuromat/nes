#!/bin/sh

echo "	INFO: makemigrations"
python3 -u manage.py makemigrations || true
echo "	INFO: Migrate"
python3 -u manage.py migrate || true
echo "	INFO: add_initial_data.py"
python3 -u manage.py shell < add_initial_data.py || true
echo "	INFO: load_initial_data.py"
python3 -u manage.py loaddata load_initial_data.json || true
python3 -u manage.py loaddata load_eeg_initial_data.json || true
echo "	INFO: create cachetable"
python3 -u manage.py createcachetable || true
echo "	INFO: create_super_user.py"
python3 -u manage.py shell < /tmp/create_superuser.py || true
echo "	INFO: import cid10"
python3 -u manage.py import_icd_cid --file icd10cid10v2017.csv || true

echo "	INFO: colectstatic"
mkdir -p static || true
python3 -u manage.py collectstatic --no-input || true

echo "  INFO: compress"
python3 -u manage.py compress --force || true

echo "	INFO: populate_history"
python3 -u manage.py populate_history --auto || true