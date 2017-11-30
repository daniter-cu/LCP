#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name lcpclient \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"54.241.136.176", "port":"8888"}' \
--profile adminuser \
outputfile_client.txt &> logs_client.txt 
