#! /bin/bash

. local_environment.list

docker stop nes
docker rm nes
docker run -dit --name nes \
    --mount type=bind,source=$ENTRYPOINT_FILE,target=/entrypoint.sh \
    -v $LIMESURVEY_CONFIG_DIR:/var/www/limesurvey/application/config \
    -v $PG_DB_DIR:/var/lib/postgresql/data \
    -v $NES_DIR:/nes \
    -p 8080:8080 -p 8000:8000 -p 5999:5432 nes
docker exec -ti nes bash