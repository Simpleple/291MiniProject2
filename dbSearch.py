from bsddb3 import db
from array import array

def searchPterms(key):
    key = key.encode('utf-8')
    database = db.DB()
    database.open("pt.idx")
    cur = database.cursor()
    a = array("i")
    data = int(cur.get(key, db.DB_SET)[1].decode('utf-8'))
    a.append(data)
    while cur.next_dup():
        data = int(cur.get(db.DB_CURRENT)[1].decode('utf-8'))
        a.append(data)
    database.close()
    return sorted(a.tolist())

print(searchPterms("soundtrack"))
