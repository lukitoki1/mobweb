import redis


class Users:
    def __init__(self, host, port):
        self.db = redis.Redis(host=host, port=port, db=0)
        self.populate()

    def populate(self):
        self.db.set("test", "123")
        self.db.set('admin', 'admin')

    def check(self, login, password):
        if self.db.get(login) is None or self.db.get(login).decode("UTF-8") != password:
            return False
        return True
