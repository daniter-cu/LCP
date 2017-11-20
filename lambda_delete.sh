#!/bin/bash -e

aws lambda delete-function \
--function-name helloworld \
--region us-west-2 \
--profile adminuser
