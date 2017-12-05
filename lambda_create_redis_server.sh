#!/bin/bash -e

aws lambda create-function \
--function-name redisserver \
--region us-west-2 \
--zip-file fileb://redis-server-package.zip \
--role arn:aws:iam::579493330882:role/service-role/testRole \
--handler redis_server.lambda_handler \
--runtime python2.7 \
--timeout 300 
