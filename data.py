import os
import re
import sys

def readOnePiece(pieceNum, index = 1):
    line = sys.stdin.readline()
    if index == 11:
        writeToFile("review.txt", '\n')
        return True
    if line == '\n':
        return False
    if index == 1:
        writeToFile("review.txt", str(pieceNum))
    if index == 2:
        writeTerms(line, pieceNum, "pterms.txt")
    if index == 7:
        writeScore(line, pieceNum)
    if index == 9:
        writeTerms(line, pieceNum, "rterms.txt")
    writeToFile("review.txt", ",")

    writeToFile("review.txt", getInfoFromStdin(line, index))
    readOnePiece(pieceNum, index + 1)
    return True
            
def writeToFile(filename, content):
    with open(filename, 'a') as file:
        file.write(content)

def getInfoFromStdin(line, index):
    line = findContentOfLine(line)
    if index in (2,5,9,10):
        line = "\"" + line + "\""
    return line

def findContentOfLine(line):
    line = line[line.find(":")+2:].strip("\n")
    line = line.replace("\"", "&quot;")
    line = line.replace("\\", "\\\\")
    return line

def writeTerms(terms, pieceNum, filename):
    terms = findContentOfLine(terms)
    for term in re.split("\W", terms):
        if len(term) > 2:
            writeToFile(filename, term.lower()+",")
            writeToFile(filename, str(pieceNum)+"\n")

def writeScore(scores, pieceNum):
    scores = findContentOfLine(scores)
    writeToFile("scores.txt", scores+",")
    writeToFile("scores.txt", str(pieceNum)+"\n")

def readAll():
    pieceNum = 1
    while sys.stdin and readOnePiece(pieceNum):
        pieceNum += 1

def clearFiles():
    try:
        os.remove("review.txt")
        os.remove("scores.txt")
        os.remove("pterms.txt")
        os.remove("rterms.txt")
    except:
        pass

clearFiles()
readAll()

