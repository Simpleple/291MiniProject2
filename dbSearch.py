from bsddb3 import db
import sys
import datetime
import time
import re
import textwrap

# Searches for a specified searchKey in a file
def exactSearch(searchKey, filename):
    # Encode the searchKey for Berkeley DB
    searchKey = searchKey.encode('utf-8')
    # Initialize the database and its cursor
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    # Initialize the result set
    resultSet = set()
    # Search for exactly the searchKey in the database
    try:
        data = cur.get(searchKey, db.DB_SET)[1].decode('utf-8')
        # If found the searchKey, add to the resultSet
        resultSet.add(int(data))
        # Add any duplicates of the searchKey from the database to resultSet
        while cur.next_dup():
            data = cur.get(db.DB_CURRENT)[1].decode('utf-8')
            resultSet.add(int(data))
    except:
        pass
    # close the database
    database.close()
    return resultSet

# Look for part of a searchKey in a specified file
def partialSearch(searchKey, filename):
    # Encode the searchKey for Berkeley DB
    encodedkey = searchKey.encode('utf-8')
    # Initialize the database and its cursor
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    # Initialize the result set
    resultSet = set()
    # Tries to find anything in the database that starts with the searchKey and
    # add to the result set
    try:
        datapair = cur.get(encodedkey, db.DB_SET_RANGE)
        data = datapair[1].decode('utf-8')
        if datapair[0].decode('utf-8').startswith(searchKey):
            resultSet.add(int(data))
        # Add any duplicates to the result set
        while str(cur.next()[0].decode('utf-8')).startswith(searchKey):
            data = cur.get(db.DB_CURRENT)[1].decode('utf-8')
            resultSet.add(int(data))
    except:
        pass
    # Close the database
    database.close()
    return resultSet

# Checks the specified file in the database for elements that are larger or 
# smaller than the searchKey. This will be used on numerical searchKeys
def rangeSearch(searchKey, filename, compare):
    # Encode the search key for Berkeley DB
    searchKey = searchKey.encode('utf-8')
    # Initialize the database and its cursor
    database = db.DB()
    database.open(filename)
    cur = database.cursor()
    # Initialize the resultSet
    resultSet = set()
    # Try to find anything in the database that is greater or less than the 
    # search key and add it to the result set
    try:
        datapair = cur.get(searchKey, db.DB_SET_RANGE)
        data = datapair[1].decode('utf-8')
        currentkey = float(datapair[0].decode('utf-8'))
        # If compare says "bigger", look for something bigger than the 
        # search key and add it to the resultSet
        if compare == "bigger":
            if currentkey > float(searchKey):
                resultSet.add(int(data))
            # Add anything bigger than the search key to the result set
            while cur.next():
                datapair = cur.get(db.DB_CURRENT)
                data = datapair[1].decode('utf-8')
                currentkey = float(datapair[0].decode('utf-8'))
                if currentkey > float(searchKey):
                    resultSet.add(int(data))
        # If compare says "less", look for anything smaller than the search key
        # and add it to the result set
        elif compare == "less":
            while cur.prev():
                datapair = cur.get(db.DB_CURRENT)
                data = datapair[1].decode('utf-8')
                currentkey = float(datapair[0].decode('utf-8'))
                if currentkey < float(searchKey):
                    resultSet.add(int(data))
    except:
        pass
    # Close the database
    database.close()
    return resultSet
    
# Open the full record of the review for the specified recordNum    
def getFullRecord(recordNum):
    # Open the database file rw.idx
    database = db.DB()
    database.open("rw.idx")
    # return the string of the record of the review for the specified recordNum,
    # encoded for Berkeley DB
    return database.get(str(recordNum).encode('utf-8'))

# Get rid of extra whitespace and any whitespace before and after 
# inequality signs
def getRidOfExtraSpace(query):
    query = re.sub(' +', ' ', query)
    query = query.replace(' > ', '>')
    query = query.replace(' < ', '<')
    return query

# Read a given query to deal with queries for matching text (rather than 
# inequalities)
def dealWithMatches(query):
    query = getRidOfExtraSpace(query)
    # Split the query by spaces after removing the extra spaces
    words = query.split(" ")
    # Initialize result list
    result = list()
    # deal with the command specified by each word in a query that is separated
    # by whitespace
    for word in words:
        # Don't touch it if it has inequalities. We'll deal with those later.
        if '>' in word or '<' in word:
            pass
        # If it's got a colon in it, it will specify a field in which to find 
        # data
        elif ':' in word:
            field = word.split(':')[0]
            data = word.split(':')[1]
            # If the data ends with %, it means that we need to search for 
            # strings that start with the characters before the % in data
            if data.endswith('%'):
                data = data.strip('%')
                # if the field is p, look for partially matching data in pt.idx
                # and add to result
                if field == 'p':
                    result.append(partialSearch(data, "pt.idx"))
                # if the field is p, look for partially matching data in rt.idx
                # and add to result
                elif field == 'r':
                    result.append(partialSearch(data, "rt.idx"))
            # If it doesn't end in %, look for fully matching strings
            else:
                # if the field is p, look for matching data in pt.idx and add 
                # to result
                if field == 'p':
                    result.append(exactSearch(data, "pt.idx"))
                # if the field is r, look for matching data in rt.idx and add
                # to result
                elif field == 'r':
                    result.append(exactSearch(data, "rt.idx"))
        # if there's no colon in the word, look for the string in both 
        # pt.idx and rt.idx
        else:
            # if word ends in %, look for words that start with the searchKey
            if word.endswith('%'):
                word = word.strip('%')
                temp = partialSearch(word, "pt.idx")
                temp = temp.union(partialSearch(word, "rt.idx"))
                result.append(temp)
            # else look for fully matching words
            else:
                temp = exactSearch(word, "pt.idx")
                temp = temp.union(exactSearch(word, "rt.idx"))
                result.append(temp)
    # Only include the data in results that is in the intersections of the
    # results for all queries
    try:
        resultSet = result[0]
        for branch in result:
            resultSet = resultSet.intersection(branch)
    # The only possible failure for the result set is when there's nothing
    # in the result list, which means that there was only inequalities.
    except:
        return {'inequalities'}
    return resultSet

# Deal with inequalities portions of queries
def dealWithInequalities(query):
    # Carry out the matching searches from queries
    resultSet = dealWithMatches(query)
    query = getRidOfExtraSpace(query)
    words = query.split(" ")
    result = list()
    # Go through each of the seperate words found in the query and deal with
    # the ones that contain inequalities
    for word in words:
        if ">" in word:
            # split at inequality
            field = word.split(">")[0]
            data = word.split(">")[1]
            # if field is "rscore, make comparison in sc.idx and append to 
            # result
            if field == "rscore":
                result.append(rangeSearch(data, "sc.idx", "bigger"))
            # if field is "pprice", check if the field is unknown or 
            # the opposite of the desired comparison and, if so, remove
            # from the existing result set
            elif field == "pprice":
                for recordNum in resultSet.copy():
                    record = getFullRecord(recordNum).decode('utf8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    if record.split(",")[2] == "unknown":
                        resultSet.remove(recordNum)
                    else:
                        actualPrice = float(record.split(",")[2])
                        if float(data) >= actualPrice:
                            resultSet.remove(recordNum)
            # if the field is "rdate", check if the query time compares in the
            # desired way with the the time in the review
            elif field == "rdate":
                for recordNum in resultSet.copy():
                    record = getFullRecord(recordNum).decode('utf-8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    reviewtime = float(record.split(",")[7])
                    querytime = time.mktime(datetime.datetime.strptime(data, "%Y/%m/%d").timetuple())
                    if reviewtime <= querytime:
                        resultSet.remove(recordNum)
        if "<" in word:
            # split at inequality            
            field = word.split("<")[0]
            data = word.split("<")[1]
            # if field is "rscore", make comparison in sc.idx and append to 
            # result
            if field == "rscore":
                result.append(rangeSearch(data, "sc.idx", "less"))
            # if field is "pprice", check if the field is unknown or 
            # the opposite of the desired comparison and, if so, remove
            # from the existing result set            
            elif field == "pprice":
                for recordNum in resultSet.copy():
                    record = getFullRecord(recordNum).decode('utf8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    if record.split(",")[2] == "unknown":
                        resultSet.remove(recordNum)
                    else:
                        actualPrice = float(record.split(",")[2])
                        if float(data) <= actualPrice:
                            resultSet.remove(recordNum)
            # if the field is "rdate", check if the query time compares in the
            # desired way with the the time in the review            
            elif field == "rdate":
                for recordNum in resultSet.copy():
                    record = getFullRecord(recordNum).decode('utf-8')
                    record = re.sub('\"[^"]+\"', '\"\"', record)
                    reviewtime = float(record.split(",")[7])
                    querytime = time.mktime(datetime.datetime.strptime(data, "%Y/%m/%d").timetuple())
                    if reviewtime >= querytime:
                        resultSet.remove(recordNum)
    # resultSet doesn't equal "inequalities", there must have been something 
    # it other than an inequality and that should be added to the result
    if resultSet != {'inequalities'}:
        result.append(resultSet)
    # Only include the data in results that is in the intersections of the
    # results for all queries
    try:
        resultSet = result[0]
        for branch in result:
            resultSet = resultSet.intersection(branch)
    except:
        return set()
    return resultSet
                    


print(readQuery("soundtrack rscore > 4"))
query = ""
try:
    # if query is "#quit", quit the program
    while query != "#quit":
        # read the query from stdin
        query = sys.stdin.readline().split("\n")[0]
        # get the appropriate resultSet
        resultSet = sorted(list(dealWithInequalities(query)))
        # index is the element in the resultset
        index = 0
        # print the output in a readable format
        for recordNum in resultSet:
            print(textwrap.fill("Review ID: " + str(resultSet[index]), 80))
            print(textwrap.fill("Product ID: " + getFullRecord(recordNum).decode('utf-8').split(",")[0].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Product Title: " + getFullRecord(recordNum).decode('utf-8').split("\"")[1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Product price: " + re.sub('\"[^\"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8')).split(",")[2].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review User ID: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8')).split(",")[3].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review Profile Name: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8'), count=1).split(",")[4][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review Helpfulness: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8')).split(",")[5].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review Score: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8')).split(",")[6].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review time: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8')).split(",")[7].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review Summary: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8'), count=2).split(",")[8][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            print(textwrap.fill("Review Text: " + re.sub('\"[^"]+\"', '\"\"', getFullRecord(recordNum).decode('utf-8'), count=3).split(",", 9)[9][1:-1].replace("&quot;", "\"").replace("\\\\", "\\"), 80))
            
            print()
            index = index + 1
except:
    print("invalid query")
