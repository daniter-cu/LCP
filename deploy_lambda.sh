#!/bin/bash -e

zip hello.py "$@"
sh lambda_create.sh

