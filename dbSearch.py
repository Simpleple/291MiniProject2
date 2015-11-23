from bsddb3 import db
import sys
import datetime
import time
import re
import textwrap

# the key in exactSearch, partialSearch and rangeSearch represents
# for the searchKey
def exactSearch(key, filename):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    try:
        data = cur.get(key, db.DB_SET)[1].decode('utf-8')
        resultSet.add(int(data))
        while cur.next_dup():
            data = cur.get(db.DB_CURRENT)[1].decode('utf-8')
            resultSet.add(int(data))
    except:
        pass
    database.close()
    return resultSet

def partialSearch(key, filename):
    encodedkey = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    try:
        datapair = cur.get(encodedkey, db.DB_SET_RANGE)
        data = datapair[1].decode('utf-8')
        if datapair[0].decode('utf-8').startswith(key):
            resultSet.add(int(data))
        while str(cur.next()[0].decode('utf-8')).startswith(key):
            data = cur.get(db.DB_CURRENT)[1].decode('utf-8')
            resultSet.add(int(data))
    except:
        pass
    database.close()
    return resultSet

def rangeSearch(key, filename, compare):
    key = key.encode('utf-8')
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    resultSet = set()
    try:
        datapair = cur.get(key, db.DB_SET_RANGE)
        data = datapair[1].decode('utf-8')
        currentkey = float(datapair[0].decode('utf-8'))
        if compare == "bigger":
            if currentkey > float(key):
                resultSet.add(int(data))
            while cur.next():
                datapair = cur.get(db.DB_CURRENT)
                data = datapair[1].decode('utf-8')
                currentkey = float(datapair[0].decode('utf-8'))
                if currentkey > float(key):
                    resultSet.add(int(data))
        elif compare == "less":
            while cur.prev():
                datapair = cur.get(db.DB_CURRENT)
                data = datapair[1].decode('utf-8')
                currentkey = float(datapair[0].decode('utf-8'))
                if currentkey < float(key):
                    resultSet.add(int(data))
    except:
        pass
    database.close()
    return resultSet
    
def getFullRecord(recno):
    database = db.DB()
    database.open("rw.idx")
    return database.get(str(recno).encode('utf-8'))

def getRidOfExtraSpace(query):
    query = re.sub(' +', ' ', query)
    query = query.replace(' > ', '>')
    query = query.replace(' < ', '<')
    return query

def readQuery(query):
    query = getRidOfExtraSpace(query)
    words = query.split(" ")
    result = list()
    for word in words:
        if '>' in word or '<' in word:
            pass
        elif ':' in word:
            field = word.split(':')[0]
            data = word.split(':')[1]
            if data.endswith('%'):
                data = data.strip('%')
                if field == 'p':
                    result.append(partialSearch(data, "pt.idx"))
                elif field == 'r':
                    result.append(partialSearch(data, "rt.idx"))
            else:
                if field == 'p':
                    result.append(exactSearch(data, "pt.idx"))
                elif field == 'r':
                    result.append(exactSearch(data, "rt.idx"))
        else:
            if word.endswith('%'):
                word = word.strip('%')
                temp = partialSearch(word, "pt.idx")
                temp = temp.union(partialSearch(word, "rt.idx"))
                result.append(temp)
            else:
                temp = exactSearch(word, "pt.idx")
                temp = temp.union(exactSearch(word, "rt.idx"))
                result.append(temp)
    try:
        resultSet = result[0]
        for branch in result:
            resultSet = resultSet.intersection(branch)
    except:
        return {'inequalities'}
    return resultSet
                    
def dealWithInequalities(query):
    resultSet = readQuery(query)
    query = getRidOfExtraSpace(query)
    words = query.split(" ")
    result = list()
    for word in words:
        if ">" in word:
            field = word.split(">")[0]
            data = word.split(">")[1]
            if field == "rscore":
                result.append(rangeSearch(data, "sc.idx", "bigger"))
            elif field == "pprice":
                for recno in resultSet.copy():
                    record = getFullRecord(recno).decode('utf8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    if record.split(",")[2] == "unknown":
                        resultSet.remove(recno)
                    else:
                        actualPrice = float(record.split(",")[2])
                        if float(data) >= actualPrice:
                            resultSet.remove(recno)
            elif field == "rdate":
                for recno in resultSet.copy():
                    record = getFullRecord(recno).decode('utf-8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    reviewtime = float(record.split(",")[7])
                    querytime = time.mktime(datetime.datetime.strptime(data, "%Y/%m/%d").timetuple())
                    if reviewtime <= querytime:
                        resultSet.remove(recno)                    
        if "<" in word:
            field = word.split("<")[0]
            data = word.split("<")[1]
            if field == "rscore":
                result.append(rangeSearch(data, "sc.idx", "less"))
            elif field == "pprice":
                for recno in resultSet.copy():
                    record = getFullRecord(recno).decode('utf8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    if record.split(",")[2] == "unknown":
                        resultSet.remove(recno)
                    else:
                        actualPrice = float(record.split(",")[2])
                        if float(data) <= actualPrice:
                            resultSet.remove(recno)
            elif field == "rdate":
                for recno in resultSet.copy():
                    record = getFullRecord(recno).decode('utf-8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    reviewtime = float(record.split(",")[7])
                    querytime = time.mktime(datetime.datetime.strptime(data, "%Y/%m/%d").timetuple())
                    if reviewtime >= querytime:
                        resultSet.remove(recno)                    
    if resultSet != {'inequalities'}:
        result.append(resultSet)
    try:
        resultSet = result[0]
        for branch in result:
            resultSet = resultSet.intersection(branch)
    except:
        return set()
    return resultSet
                    
#print(rangeSearch("4.9", "sc.idx", "less"))
#print(exactSearch("soundtrack", "pt.idx"))
#print(readQuery("iiiiii"))

query = ""
while query != "quit":
    query = sys.stdin.readline().split("\n")[0]
    resultSet = sorted(list(dealWithInequalities(query)))
    #reviewIDs = sorted(list(readQuery(query)))
    index = 0
    for recno in resultSet:
        #print(getFullRecord(recno).decode('utf-8'))
        print(textwrap.fill("Review ID: " + str(resultSet[index]), 80))
        print(textwrap.fill("Product ID: " + getFullRecord(recno).decode('utf-8').split(",")[0].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Product Title: " + getFullRecord(recno).decode('utf-8').split("\"")[1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Product price: " + re.sub('\"[^\"]+\"', '\"\"', getFullRecord(recno).decode('utf-8')).split(",")[2].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review User ID: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8')).split(",")[3].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review Profile Name: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8'), count=1).split(",")[4][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review Helpfulness: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8')).split(",")[5].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review Score: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8')).split(",")[6].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review time: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8')).split(",")[7].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review Summary: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8'), count=2).split(",")[8][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        print(textwrap.fill("Review Text: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recno).decode('utf-8'), count=3).split(",", 9)[9][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
        
        print()
        #print(getFullRecord(recno).decode('utf-8'))
        index = index + 1
