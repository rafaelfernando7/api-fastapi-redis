import redis

class RedisClient(object):

    def __init__(self, host, port):
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self.getConnection()
        return self._conn

    def getConnection(self):
        self._conn = redis.Redis(connection_pool = self.pool)
