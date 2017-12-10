#!/bin/bash -e

aws lambda delete-function \
--function-name redisclient_new \
--region us-west-2
