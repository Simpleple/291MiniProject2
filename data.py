import os
import re
import sys

def readOnePiece(pieceNum, reviews, pterms, rterms, scores, index = 1):
    line = sys.stdin.readline()
    if index == 11:
        writeToFile(reviews, '\n')
        return True
    if line == '\n' or len(line) == 0:
        return False
    if index == 1:
        writeToFile(reviews, str(pieceNum))
    if index == 2:
        writeTerms(line, pieceNum, pterms)
    if index == 7:
        writeScore(line, pieceNum, scores)
    if index == 9:
        writeTerms(line, pieceNum, rterms)
    if index == 10:
        writeTerms(line, pieceNum, rterms)
    writeToFile(reviews, ",")

    writeToFile(reviews, getInfoFromStdin(line, index))
    readOnePiece(pieceNum, reviews, pterms, rterms, scores, index + 1)
    return True
            
def writeToFile(filename, content):
    filename.write(content)

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

def writeScore(line, pieceNum, scores):
    line = findContentOfLine(line)
    writeToFile(scores, line+",")
    writeToFile(scores, str(pieceNum)+"\n")

def readAll():
    with open("reviews.txt", 'a') as review:
        with open("pterms.txt", 'a') as pterms:
            with open("rterms.txt", 'a') as rterms:
                with open("scores.txt", 'a') as scores:            
                    pieceNum = 1
                    while sys.stdin and readOnePiece(pieceNum, review, pterms, rterms, scores):
                        pieceNum += 1

def clearFiles():
    try:
        os.remove("reviews.txt")
        os.remove("scores.txt")
        os.remove("pterms.txt")
        os.remove("rterms.txt")
    except:
        pass

clearFiles()
readAll()

