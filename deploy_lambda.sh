#!/bin/bash -e

zip -r hello.zip server_tcp.py structs.py redis.conf redis-server
sh lambda_create.sh

