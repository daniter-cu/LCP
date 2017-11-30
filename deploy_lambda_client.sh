#!/bin/bash -e

zip client-package.zip client.py structs.py
sh lambda_create_client.sh

