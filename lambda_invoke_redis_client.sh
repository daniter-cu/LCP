#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name redisclient \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"52.53.149.33", "port":"8888", "bind_port": "'$1'"}' \
--profile adminuser \
outputfile_redis_client.txt > $2 2>&1 
