#!/bin/bash -e

aws lambda delete-function \
--function-name lcpserver \
--region us-west-2 \
--profile adminuser
