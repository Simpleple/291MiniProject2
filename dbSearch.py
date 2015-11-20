from bsddb3 import db

def exactSearch(key, filename):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    data = int(cur.get(key, db.DB_SET)[1].decode('utf-8'))
    resultSet.add(data)
    while cur.next_dup():
        data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
        resultSet.add(data)
    database.close()
    return resultSet

def partialSearch(key, filename):
    encodedkey = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    data = int(cur.get(encodedkey, db.DB_SET_RANGE)[1].decode('utf-8'))
    resultSet.add(data)
    while str(cur.next()[0].decode('utf-8')).startswith(key):
        data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
        resultSet.add(data)
    database.close()
    return resultSet

def rangeSearch(key, filename, compare):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    data = int(cur.get(key, db.DB_SET_RANGE)[1].decode('utf-8'))
    if compare == "bigger":
        resultSet.add(data)
        while cur.next():
            data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
            resultSet.add(data)
    elif compare == "less":
        while cur.prev():
            data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
            resultSet.add(data)
    database.close()
    return resultSet
    
def printFullRecord(recno):
    database = db.DB()
    database.open("rw.idx")
    print(database.get(recno.encode('utf-8')))
    database.close()

#print(rangeSearch("4.9", "sc.idx", "less"))
#print(exactSearch("soundtrack", "pt.idx"))
printFullRecord("1")
