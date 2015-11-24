import os
import sys

# Convert input records into the format db_load expects

inputFile = sys.argv[1]
outputFile = sys.argv[2]

# Get rid of output files of the same name if they exist already
try:
    os.remove(outputFile)
except:
    pass

# Format the file
with open(inputFile, "r") as f1:
    with open(outputFile, "a") as f2:
        for line in f1:
            line = line.strip("\n")
            comma = line.find(",")
            f2.write(line[:comma]+"\n")
            f2.write(line[comma+1:]+"\n")
