#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name redisserver \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"54.212.247.168", "port":"8888"}' \
outputfile.txt > logs.txt 2>&1
