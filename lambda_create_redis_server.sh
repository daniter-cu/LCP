#!/bin/bash -e

aws lambda create-function \
--function-name redisserver \
--region us-west-1 \
--zip-file fileb://redis-server-package.zip \
--role arn:aws:iam::569818935723:role/pywren_exec_role_1 \
--handler redis_server.lambda_handler \
--runtime python2.7 \
--timeout 30 
