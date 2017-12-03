#!/bin/bash

mkdir deps
cd deps
git clone https://github.com/antirez/redis.git
git checkout 4.0
cd redis
make CFLAGS="-static" EXEEXT="-static" LDFLAGS="-I/usr/local/include/"
cp src/redis-server ../../
