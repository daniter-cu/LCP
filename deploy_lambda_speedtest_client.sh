#!/bin/bash -e

zip -r redis-client-package.zip speed_test.py redis redis-2.10.6.dist-info
sh lambda_create_speedtest_client.sh

