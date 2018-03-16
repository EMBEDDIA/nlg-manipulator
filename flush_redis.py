import os
import urllib.parse
import redis
url = urllib.parse.urlparse(os.environ.get('REDISCLOUD_URL'))
cache = redis.Redis(host=url.hostname, port=url.port, password=url.password)
cache.flushdb()