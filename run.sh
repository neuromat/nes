#! /bin/bash

docker stop nes
docker rm nes
# docker run -it --name nes --volume /home/dreese/Proyectos/dreese/development/FPUNA/nes-1:/nes/ -p 8080:8080 -p 8000:8000 -p 5999:5432 --entrypoint '/bin/sh' nes
# docker run -it --name nes -v /home/dreese/Proyectos/dreese/development/FPUNA/volumes/postgres_db:/var/lib/postgresql/data -v /home/dreese/Proyectos/dreese/development/FPUNA/nes-1:/nes -p 8080:8080 -p 8000:8000 -p 5999:5432 nes
docker run -dit --name nes \
    --mount type=bind,source=/home/dreese/Proyectos/dreese/development/FPUNA/nes-1/entrypoint_local_development.sh,target=/entrypoint.sh \
    -v /home/dreese/Proyectos/dreese/development/FPUNA/volumes/limesurvey:/var/www/limesurvey/application/config \
    -v /home/dreese/Proyectos/dreese/development/FPUNA/volumes/postgres_db:/var/lib/postgresql/data \
    -v /home/dreese/Proyectos/dreese/development/FPUNA/nes-1:/nes \
    -p 8080:8080 -p 8000:8000 -p 5999:5432 nes
docker exec -ti nes bash