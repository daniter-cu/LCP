#!/bin/bash -e

aws lambda delete-function \
--function-name redisserver_new \
--region us-west-2 \
