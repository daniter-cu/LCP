#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name redisserver \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"52.53.149.33", "port":"8888", "connect_port":"'$1'"}' \
--profile adminuser \
outputfile.txt > $2 2>&1
