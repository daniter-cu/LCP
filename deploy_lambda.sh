#!/bin/bash -e

zip hello.zip server.py structs.py
sh lambda_create.sh

