#!/bin/bash -e

zip -r hello.zip redis_server.py structs.py redis.conf redis-server
sh lambda_create_redis_server.sh
