#!/bin/bash
docker-compose up --detach mariadb-server mysql-server postgres-server
docker-compose up opencsv-client
docker-compose up csvcommons-client
docker-compose up univocity-client
docker-compose up pycsv-client
docker-compose up pandas-client
docker-compose up duckdb-client
docker-compose up rcsv-client
docker-compose up clevercs-client
docker-compose up rhypoparsr-client
docker-compose up libreoffice-client
docker-compose up sqlite-client

docker-compose up postgres-client
docker-compose up mariadb-client
docker-compose up mysql-client
