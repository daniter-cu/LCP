#!/bin/bash -e

aws lambda delete-function \
--function-name redisserver \
--region us-west-2 \
