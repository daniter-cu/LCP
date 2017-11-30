#!/bin/bash -e

zip hello.zip server_tcp.py structs.py
sh lambda_create.sh

