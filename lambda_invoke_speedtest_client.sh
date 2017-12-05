#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name speedtest \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"13.57.29.101", "port":"8888", "bind_port": "'$1'"}' \
--cli-read-timeout 300 \
outputfile_speedtest_client.txt > $2 2>&1 
