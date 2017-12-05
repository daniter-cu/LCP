#!/bin/bash -e

aws lambda create-function \
--function-name speedtest \
--region us-west-2 \
--zip-file fileb://redis-client-package.zip \
--role arn:aws:iam::579493330882:role/service-role/testRole \
--handler speed_test.lambda_handler \
--runtime python2.7 \
--timeout 300
