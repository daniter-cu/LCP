#!/bin/bash -e

aws lambda delete-function \
--function-name lcpclient \
--region us-west-2 \
--profile adminuser
