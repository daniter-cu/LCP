#!/bin/bash -e

aws lambda delete-function \
--function-name redisclient \
--region us-west-1
