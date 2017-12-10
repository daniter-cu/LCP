#!/bin/bash

# arg1: number of servers to run concurrently

for i in $(seq 0 $(($1-1)))
do
	#sh lambda_invoke_redis_server.sh $((6000+$i)) logs$i.txt &
	sh lambda_invoke_redis_client.sh $((8000+$i)) 
done
