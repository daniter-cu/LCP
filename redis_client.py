from redis import Redis

def lambda_handler(event, context):
    redis = Redis(event['ip'], int(event['port']))
    redis.set('foo', 'a')
    print redis.get('a')
