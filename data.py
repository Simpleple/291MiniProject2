import os
import re
import sys

# Take in a line of data and decide how to handle each part of it, 
# writing it to files as it goes. index is used to keep track of the line
# of the current review
def readOnePiece(reviewNum, reviews, pterms, rterms, scores, index = 1):
    # Read a line from the file
    line = sys.stdin.readline()
    
    # if at the last line of this review, write a newline to reviews.txt
    # and continue onto the next review
    if index == 11:
        writeToFile(reviews, '\n')
        return True
    
    # if a blank line, there must have been more than one blank line in a row, signifying
    # the end of the file, so don't write anything and return False to end the readAll function
    if line == '\n' or len(line) == 0:
        return False
    
    # if this is the first line of this review, write the number of the review to reviews.txt
    if index == 1:
        writeToFile(reviews, str(reviewNum))

    # if this is the second line of this review, write the appropriate terms to pterms
    if index == 2:
        writeTerms(line, reviewNum, pterms)
  
    # if this is the seventh line of this review, write the appropriate terms to scores
    if index == 7:
        writeScore(line, reviewNum, scores)

    # if this is the ninth line of this review, write the appropriate terms to rterms
    if index == 9:
        writeTerms(line, reviewNum, rterms)

    # if this is the tenth line of this review, write the appropriate terms to rterms
    if index == 10:
        writeTerms(line, reviewNum, rterms)
    
    # write a comma after whatever information was entered last to seperate the data
    # in reviews
    writeToFile(reviews, ",")

    # Write the necessary formatted info to reviews
    writeToFile(reviews, getInfoFromStdin(line, index))

    # recursively call self, increasing index to go through each line of this review
    readOnePiece(reviewNum, reviews, pterms, rterms, scores, index + 1)
    return True
            
# Write specified content to the specified file
def writeToFile(filename, content):
    filename.write(content)

# Get the content of a line and decide whether or not to add double quotes
# to the beginning and end of the string, depending on which part of the 
# line it is
def getInfoFromStdin(line, index):
    line = findContentOfLine(line)

    # if the element is one of the following indexed sections of the line, 
    # it requires double quotes on the beginning and end of the string
    if index in (2,5,9,10):
        line = "\"" + line + "\""
    return line

# Find the useful content of lines and format them according to specifications
def findContentOfLine(line):
    # Needed info in the lines always starts on the second character after a colon
    line = line[line.find(":")+2:].strip("\n")

    # Make the replacements in the string to allow as input for Berkeley DB and to 
    # allow double quotes to be used to encode character strings
    line = line.replace("\"", "&quot;")
    line = line.replace("\\", "\\\\")
    return line

# write any terms that are longer than two characters in a given line to the specified
# file, followed by a comma and which review its from
def writeTerms(terms, reviewNum, filename):
    terms = findContentOfLine(terms)

    # split by word
    for term in re.split("\W", terms):
        # Check if three characters or longer
        if len(term) > 2:
            # write it in lowercase followed by a comma, the review ID and a newline
            writeToFile(filename, term.lower()+",")
            writeToFile(filename, str(reviewNum)+"\n")

# write scores to the scores.txt file in the appropriate format
def writeScore(line, reviewNum, scores):
    # get the content of the line
    line = findContentOfLine(line)
    # write the score followed by a comma, the review ID and newline
    writeToFile(scores, line+",")
    writeToFile(scores, str(reviewNum)+"\n")

# Read all of the lines in the file
def readAll():
    # Open the files that will be written
    with open("reviews.txt", 'a') as review:
        with open("pterms.txt", 'a') as pterms:
            with open("rterms.txt", 'a') as rterms:
                with open("scores.txt", 'a') as scores:
                    # reviewNum is used to count the reviews in the file
                    reviewNum = 1

                    # Go through the file while there's file to be read and readOnePiece returns True
                    while sys.stdin and readOnePiece(reviewNum, review, pterms, rterms, scores):
                        reviewNum += 1

# Try to remove the output files if they have already been written
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

