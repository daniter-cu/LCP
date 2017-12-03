#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name redisclient \
--region us-west-1 \
--log-type Tail \
--payload '{"ip":"54.212.247.168", "port":"8888", "bind_port": "'$1'"}' \
outputfile_redis_client.txt > $2 2>&1 
