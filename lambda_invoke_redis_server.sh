#!/bin/bash -e

aws lambda invoke \
--invocation-type Event \
--function-name redisserver_new \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"54.212.247.168", "port":"8888", "connect_port":"'$1'"}' \
--cli-read-timeout 400 \
outputfile.txt
#outputfile.txt > $2 2>&1
