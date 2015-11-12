import os
import sys

inputFile = sys.argv[1]
outputFile = sys.argv[2]

try:
    os.remove(outputFile)
except:
    pass

with open(inputFile, "r") as f1:
    for line in f1:
        line = line.strip("\n")
        comma = line.find(",")
        with open(outputFile, "a") as f2:
            f2.write(line[:comma]+"\n")
            f2.write(line[comma+1:]+"\n")
