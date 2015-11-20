from bsddb3 import db
from array import array

def exactSearch(key, filename):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    a = array("i")
    data = int(cur.get(key, db.DB_SET)[1].decode('utf-8'))
    a.append(data)
    while cur.next_dup():
        data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
        a.append(data)
    database.close()
    return sorted(a.tolist())

def partialSearch(key, filename):
    encodedkey = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    a = array("i")
    data = int(cur.get(encodedkey, db.DB_SET_RANGE)[1].decode('utf-8'))
    a.append(data)
    while str(cur.next()[0].decode('utf-8')).startswith(key):
        data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
        a.append(data)
    database.close()
    return sorted(a.tolist())

def rangeSearch(key, filename, compare):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    a = array("i")
    data = int(cur.get(key, db.DB_SET_RANGE)[1].decode('utf-8'))
    if compare == "bigger":
        a.append(data)
        while cur.next():
            data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
            a.append(data)
    elif compare == "less":
        while cur.prev():
            data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
            a.append(data)
    database.close()
    return sorted(a.tolist())
    
print(rangeSearch("4.9", "sc.idx", "less"))
