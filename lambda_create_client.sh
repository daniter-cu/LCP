#!/bin/bash -e

aws lambda create-function \
--function-name lcpclient \
--region us-west-2 \
--zip-file fileb://client-package.zip \
--role arn:aws:iam::579493330882:role/service-role/testRole \
--handler client_tcp.lambda_handler \
--runtime python2.7 \
--timeout 30 \
--profile adminuser 
