from pymongo import MongoClient


class MongoDataBase(object):
    def __init__(self):
        self.conn = MongoClient('192.168.1.231', 27017)
        self.conn.admin.authenticate('root', 'twd@root$9921')
        self.coll = self.conn['datamall-db']['data_type_info']

    def insert(self, result):
        res = self.coll.insert_one(result)
        return res

    def find(self, result=None):
        res = self.coll.find(result)
        return res


if __name__ == '__main__':
    MongoDataBase().insert({"name": "xingming"})
