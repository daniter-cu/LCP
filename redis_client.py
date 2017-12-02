from redis import Redis


def lambda_handler(event, context):
    redis = Redis(event['ip'], int(event['port']))
    a = redis.set('foo', 'a')
    print "Redis set reply: ", a
    foo = redis.get('foo')
    print "Redis get reply: ", foo
