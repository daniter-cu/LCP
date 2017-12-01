#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name redisclient \
--region us-west-1 \
--log-type Tail \
--payload '{"ip":"13.57.41.133", "port":"8888"}' \
outputfile_redis_client.txt &> logs_redis_client.txt
