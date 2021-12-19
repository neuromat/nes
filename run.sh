#! /bin/bash

. local_environment.list

if [ ! -z $1 ] && [ $1 = "--clean" ]
then
  echo "###########################"
  echo "Cleaning existing container"
  echo "###########################"
  docker stop nes
  docker rm -f nes
fi

{
  echo "###########################"
  echo "Trying to start container"
  echo "###########################"
  docker start nes
} || {
  echo "###########################"
  echo "Failed to start container."
  echo "Creating a new container."
  echo "###########################"
  docker run -dit --name nes \
      --mount type=bind,source=$ENTRYPOINT_FILE,target=/entrypoint.sh \
      -v $LIMESURVEY_CONFIG_DIR:/var/www/limesurvey/application/config \
      -v $PG_DB_DIR:/var/lib/postgresql/data \
      -v $NES_DIR:/nes \
      -p 8080:8080 -p 8000:8000 -P -p 127.0.0.1:5999:5432 nes
}
docker exec -ti nes bash
#docker run -ti --name nes --entrypoint /bin/bash -v $NES_DIR:/nes nes

# postgresql.conf =>     listen_address = '*'
# pg_hba.conf =>      host all all 0.0.0.0/0 trust

# Set postgres pass => ALTER USER user_name WITH PASSWORD 'new_password';