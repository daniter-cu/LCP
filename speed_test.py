from redis import Redis
import os
import time
import boto3

bucket_name = 'd8j32l5-bucket022861'

def do_read_test(size, data, redis):
    times = []
    runs = 100
    key = "TESTKEY"
    redis.set(key, data)
    for i in xrange(runs):
        start = time.time()
        redis.get(key)
        stop = time.time()
        times.append(stop - start)
    print "RESULT READ: Size", size, "averge time : ", (sum(times) / len(times))


def do_write_test(size, data, redis):
    times = []
    runs = 100
    key = "TESTKEY"
    for i in xrange(runs):
        start = time.time()
        redis.set(key, data)
        stop = time.time()
        times.append(stop - start)
    print "RESULT WRITE: Size", size, "averge time : ", (sum(times) / len(times))

def do_write_s3_test(size, data, s3_client):
    times = []
    runs = 100
    for i in xrange(runs):
        start = time.time()
        s3_client.put_object(
                Bucket = bucket_name,
                Body = data,
                Key = 'DANITER_TEST_'+ str(size)
            )
        stop = time.time()
        times.append(stop - start)
    print "RESULT WRITE: Size", size, "averge time : ", (sum(times) / len(times))

def do_read_s3_test(size, s3_client):
    times = []
    runs = 100
    for i in xrange(runs):
        start = time.time()
        s3_client.get_object(
                Bucket = bucket_name,
                Key = 'DANITER_TEST_'+ str(size)
            )['Body'].read()
        stop = time.time()
        times.append(stop - start)
    print "RESULT READ: Size", size, "averge time : ", (sum(times) / len(times))


def lambda_handler(event, context):
    # redis = Redis(event['ip'], int(event['port']),
    #               bind_port=int(event['bind_port']))
    # a = redis.set('foo', 'a')
    # foo = redis.get('foo')
    # sizes = [1, 1024, 1024*10, 1024*100, 1024*1024 ]#[1024*1024*10, 1024*1024*100] #
    # data = "a"*(sizes[-1])
    # for s in sizes:
    #     do_read_test(s, data[:s], redis)
    #     do_write_test(s, data[:s], redis)
    sizes = [1024*10, 1024*100, 1024*1024 ]
    data = "a"*(sizes[-1])
    s3_client = boto3.client('s3')
    for s in sizes:
        do_write_s3_test(s, data[:s], s3_client)
        do_read_s3_test(s, s3_client)


if __name__=='__main__':
    class Redis(object):
        def get(self, a):
            # for i in xrange(10000):
            #     x = i / 1000* i**2
            pass

        def set(self, a, b):
            pass
    lambda_handler(None, None)
