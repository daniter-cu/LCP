#!/bin/bash -e

zip client-package.zip client_tcp.py structs.py
sh lambda_create_client.sh

