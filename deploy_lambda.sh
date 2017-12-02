#!/bin/bash -e

zip -r hello.zip server_tcp.py structs.py redis.conf redis-server
#redis redis-2.10.6.dist-info
sh lambda_create.sh

