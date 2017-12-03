#!/bin/bash -e

zip -r redis-client-package.zip redis_client.py redis redis-2.10.6.dist-info
sh lambda_create_redis_client.sh

