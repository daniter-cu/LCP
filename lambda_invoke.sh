#!/bin/bash -e

aws lambda invoke \
--invocation-type RequestResponse \
--function-name lcpserver \
--region us-west-2 \
--log-type Tail \
--payload '{"ip":"54.153.96.14", "port":"8888"}' \
--profile adminuser \
outputfile.txt &> logs.txt 
