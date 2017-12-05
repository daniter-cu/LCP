from redis import Redis


def lambda_handler(event, context):
    redis = Redis(event['ip'], int(event['port']),
                  bind_port=int(event['bind_port']))
    foo = 'a' * 1024 * 100
    a = redis.set('foo', foo)
    print "Redis set reply: ", a
    a = redis.set('boo', foo)
    print "Redis set reply: ", a
    foo = redis.get('foo')
    print "Redis get reply: ", foo
    foo = redis.get('boo')
    print "Redis get reply: ", foo
