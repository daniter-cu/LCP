#!/bin/bash -e

aws lambda delete-function \
--function-name speedtest \
--region us-west-2
