from redis import Redis
import os
import time


def do_read_test(size, data, redis):
    times = []
    runs = 1
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
    runs = 1
    key = "TESTKEY"
    for i in xrange(runs):
        start = time.time()
        redis.set(key, data)
        stop = time.time()
        times.append(stop - start)
    print "RESULT WRITE: Size", size, "averge time : ", (sum(times) / len(times))

def lambda_handler(event, context):
    redis = Redis(event['ip'], int(event['port']),
                  bind_port=int(event['bind_port']))
    a = redis.set('foo', 'a')
    foo = redis.get('foo')
    print "starting", time.time()
    sizes = [1, 1024, 1024*10, 1024*100, 1024*1024, 1024*1024*10]#, 1024*1024*100]
    data = "a"*(sizes[-1])
    print "about to loop", time.time()
    for s in sizes:
        print "start loop", time.time()
        do_read_test(s, data[:s], redis)
        print "after read", time.time()
        do_write_test(s, data[:s], redis)
        print "after write", time.time()


if __name__=='__main__':
    class Redis(object):
        def get(self, a):
            # for i in xrange(10000):
            #     x = i / 1000* i**2
            pass

        def set(self, a, b):
            pass
    lambda_handler(None, None)
