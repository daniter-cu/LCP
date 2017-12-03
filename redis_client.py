from redis import Redis


def lambda_handler(event, context):
    redis = Redis(event['ip'], int(event['port']),
                  bind_port=int(event['bind_port']))
    a = redis.set('foo', 'a')
    print "Redis set reply: ", a
    a = redis.set('boo', 'b')
    print "Redis set reply: ", a
    foo = redis.get('foo')
    print "Redis get reply: ", foo
    foo = redis.get('boo')
    print "Redis get reply: ", foo
