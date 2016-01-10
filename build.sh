#!/usr/bin/env bash

docker-compose build base
docker-compose build app celery celerybeat
