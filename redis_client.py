from redis import Redis


def lambda_handler(event, context):
    import time

    t1 = time.time()
    redis = Redis(event['ip'], int(event['port']),
                  bind_port=int(event['bind_port']))
    #foo = 'a' * 1024 * 100
    value = 'v' * 4096

    for i in range(500):
        key = 'shuffle' + str(event['bind_port']) + str(i)
        result = redis.set(key, value)
    t2 = time.time()

    return t2-t1
