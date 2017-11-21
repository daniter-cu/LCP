#!/bin/bash -e

zip hello.zip "$@"
sh lambda_create.sh

