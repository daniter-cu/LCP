#!/bin/bash -e

aws lambda create-function \
--function-name lcpserver \
--region us-west-2 \
--zip-file fileb://hello.zip \
--role arn:aws:iam::579493330882:role/service-role/testRole \
--handler server.lambda_handler \
--runtime python2.7 \
--timeout 30 \
--profile adminuser 
