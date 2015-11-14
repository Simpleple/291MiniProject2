from bsddb3 import db

database = db.DB()
database.open("sc.idx")
cur = database.cursor()
iter = cur.first()
while iter:
    print(iter)
    iter = cur.next()
cur.close()
print(database.get(b'3.0'))
database.close()
